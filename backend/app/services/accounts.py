from datetime import datetime, timezone
from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from sqlalchemy import select
from app.core.config import get_settings
from app.core.errors import BusinessError
from app.core.security import hash_password, verify_password, create_access_token
from app.models import User, PasswordResetRequest
from app.repositories.accounts import AccountRepository
from app.schemas.auth import UserOut

class RateLimiter:
    def __init__(self):
        self.events = defaultdict(deque)
        self.lock = Lock()

    def check(self, key):
        now = monotonic()
        settings = get_settings()
        with self.lock:
            # Remove inactive keys so public endpoints cannot grow state indefinitely.
            for old_key in list(self.events):
                queue = self.events[old_key]
                while queue and queue[0] <= now-settings.auth_rate_window_seconds:
                    queue.popleft()
                if not queue:
                    del self.events[old_key]
            queue = self.events[key]
            if len(queue) >= settings.auth_rate_limit:
                raise BusinessError(429, 'Quá nhiều yêu cầu. Vui lòng thử lại sau.')
            queue.append(now)

rate_limiter = RateLimiter()

class AccountService:
    def __init__(self, db):
        self.db = db
        self.repo = AccountRepository(db)

    def login(self, data):
        user = self.repo.by_email(data.email)
        if user is None or not user.trang_thai or not verify_password(data.password,user.mat_khau_hash):
            raise BusinessError(401, 'Email hoặc mật khẩu không đúng.')
        return dict(access_token=create_access_token(user), token_type='bearer', user=UserOut.model_validate(user))

    def get(self, user_id, lock=False):
        user = self.repo.get(user_id,lock)
        if user is None:
            raise BusinessError(404,'Không tìm thấy tài khoản.')
        return user

    def profile(self,user,data):
        user = self.get(user.id,True)
        values=data.model_dump(exclude_unset=True)
        if values.get('ho_ten', 'ok') is None:
            raise BusinessError(422,'Họ tên không được để trống.')
        for key,value in values.items():
            setattr(user,key,value)
        self.db.commit()
        return user

    def create(self,data):
        if self.repo.by_email(data.email):
            raise BusinessError(409,'Email đã tồn tại.')
        values=data.model_dump(exclude={'password'})
        user=User(**values,mat_khau_hash=hash_password(data.password),must_change_password=True)
        self.db.add(user)
        self.db.commit()
        return user

    def update(self,actor,user_id,data):
        self.repo.lock_admin_changes()
        user=self.get(user_id,True)
        values=data.model_dump(exclude_unset=True)
        for required in ('ho_ten','email','vai_tro','trang_thai'):
            if required in values and values[required] is None:
                raise BusinessError(422,'Trường bắt buộc không được để trống.')
        removes_admin = user.vai_tro=='ADMIN' and (values.get('vai_tro',user.vai_tro)!='ADMIN' or values.get('trang_thai',user.trang_thai) is False)
        if removes_admin and (actor.id==user.id or (user.trang_thai and self.repo.active_admin_count()<=1)):
            raise BusinessError(409,'Không thể khóa hoặc hạ quyền quản trị viên này.')
        if 'email' in values:
            existing=self.repo.by_email(values['email'])
            if existing and existing.id!=user.id:
                raise BusinessError(409,'Email đã tồn tại.')
        if any(key in values and values[key]!=getattr(user,key) for key in ('vai_tro','trang_thai')):
            user.auth_version+=1
        for key,value in values.items():
            setattr(user,key,value)
        self.db.commit()
        return user

    def change_password(self,user,data):
        user=self.get(user.id,True)
        if not verify_password(data.current_password,user.mat_khau_hash):
            raise BusinessError(409,'Mật khẩu hiện tại không đúng.')
        if verify_password(data.new_password,user.mat_khau_hash):
            raise BusinessError(422,'Mật khẩu mới phải khác mật khẩu hiện tại.')
        user.mat_khau_hash=hash_password(data.new_password)
        user.must_change_password=False
        user.auth_version+=1
        self.db.commit()
        return {'detail':'Đổi mật khẩu thành công. Vui lòng đăng nhập lại.'}

    def reset_password(self,user_id,password,commit=True):
        user=self.get(user_id,True)
        user.mat_khau_hash=hash_password(password)
        user.must_change_password=True
        user.auth_version+=1
        if commit:
            self.db.commit()
        return {'detail':'Đã đặt lại mật khẩu.'}

    def logout(self,user):
        user=self.get(user.id,True)
        user.auth_version+=1
        self.db.commit()
        return {'detail':'Đã đăng xuất.'}

    def forgot(self,email):
        user=self.repo.by_email(email)
        if user and user.trang_thai:
            user=self.get(user.id,True)
            if not self.repo.pending_reset(user.id):
                self.db.add(PasswordResetRequest(nguoi_dung_id=user.id))
                self.db.commit()
        return {'detail':'Nếu tài khoản hợp lệ, yêu cầu đã được gửi đến quản trị viên.'}

    def resolve(self,actor,request_id,data):
        record=self.db.scalar(select(PasswordResetRequest).where(PasswordResetRequest.id==request_id).with_for_update())
        if not record:
            raise BusinessError(404,'Không tìm thấy yêu cầu.')
        if record.trang_thai!='PENDING':
            raise BusinessError(409,'Yêu cầu đã được xử lý.')
        if not data.reject and not data.new_password:
            raise BusinessError(422,'Cần nhập mật khẩu mới.')
        if not data.reject:
            self.reset_password(record.nguoi_dung_id,data.new_password,commit=False)
        record.trang_thai='REJECTED' if data.reject else 'RESOLVED'
        record.ngay_xu_ly=datetime.now(timezone.utc)
        record.admin_id=actor.id
        self.db.commit()
        return {'detail':'Đã xử lý yêu cầu.'}
