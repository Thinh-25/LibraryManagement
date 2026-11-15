from sqlalchemy import select, func, text, or_
from app.models import User, PasswordResetRequest

class AccountRepository:
    def __init__(self, db):
        self.db = db

    def by_email(self, email):
        return self.db.scalar(select(User).where(func.lower(User.email) == email.lower()))

    def get(self, user_id, lock=False):
        query = select(User).where(User.id == user_id)
        if lock:
            query = query.with_for_update().execution_options(populate_existing=True)
        return self.db.scalar(query)

    def users(self, page, page_size, search=None):
        query = select(User)
        if search:
            pattern = '%' + search + '%'
            query = query.where(or_(User.ho_ten.ilike(pattern),User.email.ilike(pattern)))
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        return self.db.scalars(query.order_by(User.id).offset((page-1)*page_size).limit(page_size)).all(), total

    def lock_admin_changes(self):
        # One transaction advisory lock serializes all administrator role/status changes.
        self.db.execute(text('SELECT pg_advisory_xact_lock(763819234)'))

    def active_admin_count(self):
        return self.db.scalar(select(func.count()).select_from(User).where(User.vai_tro=='ADMIN',User.trang_thai.is_(True)))

    def pending_reset(self,user_id):
        return self.db.scalar(select(PasswordResetRequest).where(PasswordResetRequest.nguoi_dung_id==user_id,PasswordResetRequest.trang_thai=='PENDING'))

    def resets(self,page,page_size):
        query = select(PasswordResetRequest, User.ho_ten, User.email).join(User, User.id==PasswordResetRequest.nguoi_dung_id)
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        rows = self.db.execute(query.order_by(PasswordResetRequest.id.desc()).offset((page-1)*page_size).limit(page_size)).all()
        return [dict(id=r.id,nguoi_dung_id=r.nguoi_dung_id,trang_thai=r.trang_thai,ngay_tao=r.ngay_tao,ngay_xu_ly=r.ngay_xu_ly,admin_id=r.admin_id,ho_ten=name,email=email) for r,name,email in rows],total
