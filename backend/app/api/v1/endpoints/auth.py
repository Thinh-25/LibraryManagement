from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.auth import Login, EmailInput, ProfileUpdate, PasswordChange, UserOut
from app.services.accounts import AccountService, rate_limiter

router = APIRouter(prefix='/auth', tags=['Xác thực'])

@router.post('/login')
def login(data: Login, request: Request, db: Session=Depends(get_db)):
    rate_limiter.check(('login',request.client.host if request.client else 'unknown'))
    return AccountService(db).login(data)

@router.post('/forgot-password')
def forgot(data: EmailInput, request: Request, db: Session=Depends(get_db)):
    rate_limiter.check(('forgot',request.client.host if request.client else 'unknown'))
    return AccountService(db).forgot(data.email)

@router.get('/me',response_model=UserOut)
def me(user: User=Depends(get_current_user)):
    return user

@router.patch('/me',response_model=UserOut)
def profile(data: ProfileUpdate,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    if user.must_change_password:
        from app.core.errors import BusinessError
        raise BusinessError(403,'Vui lòng đổi mật khẩu trước khi tiếp tục.')
    return AccountService(db).profile(user,data)

@router.post('/change-password')
def change_password(data: PasswordChange,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    return AccountService(db).change_password(user,data)

@router.post('/logout')
def logout(user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    return AccountService(db).logout(user)
