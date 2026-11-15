from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jwt import InvalidTokenError
from app.core.errors import BusinessError
from app.core.security import decode_access_token
from app.dependencies.database import get_db
from app.models import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        if credentials is None:
            raise ValueError()
        claims = decode_access_token(credentials.credentials)
        user = db.get(User, int(claims['sub']))
        if user is None or not user.trang_thai or user.auth_version != claims['ver']:
            raise ValueError()
    except (InvalidTokenError, ValueError, KeyError, TypeError):
        raise BusinessError(401, 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn.')
    allowed = {'/api/v1/auth/me','/api/v1/auth/change-password','/api/v1/auth/logout'}
    if user.must_change_password and request.url.path not in allowed:
        raise BusinessError(403, 'Vui lòng đổi mật khẩu trước khi tiếp tục.')
    return user


def require_roles(*roles):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.vai_tro not in roles:
            raise BusinessError(403, 'Bạn không có quyền thực hiện thao tác này.')
        return user
    return dependency
