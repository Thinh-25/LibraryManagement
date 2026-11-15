from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models import User
from app.schemas.auth import UserCreate, UserUpdate, UserOut, PasswordReset, ResolveRequest
from app.services.accounts import AccountService

router=APIRouter(tags=['Tài khoản'])
admin=require_roles('ADMIN')

@router.get('/users')
def users(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),search:str|None=None,user:User=Depends(admin),db:Session=Depends(get_db)):
    items,total=AccountService(db).repo.users(page,page_size,search)
    return dict(items=[UserOut.model_validate(item) for item in items],total=total,page=page,page_size=page_size)

@router.post('/users',response_model=UserOut,status_code=201)
def create(data:UserCreate,user:User=Depends(admin),db:Session=Depends(get_db)):
    return AccountService(db).create(data)

@router.get('/users/{user_id}',response_model=UserOut)
def detail(user_id:int,user:User=Depends(admin),db:Session=Depends(get_db)):
    return AccountService(db).get(user_id)

@router.patch('/users/{user_id}',response_model=UserOut)
def update(user_id:int,data:UserUpdate,user:User=Depends(admin),db:Session=Depends(get_db)):
    return AccountService(db).update(user,user_id,data)

@router.post('/users/{user_id}/reset-password')
def reset(user_id:int,data:PasswordReset,user:User=Depends(admin),db:Session=Depends(get_db)):
    return AccountService(db).reset_password(user_id,data.new_password)

@router.get('/password-reset-requests')
def resets(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user:User=Depends(admin),db:Session=Depends(get_db)):
    items,total=AccountService(db).repo.resets(page,page_size)
    return dict(items=items,total=total,page=page,page_size=page_size)

@router.post('/password-reset-requests/{request_id}/resolve')
def resolve(request_id:int,data:ResolveRequest,user:User=Depends(admin),db:Session=Depends(get_db)):
    return AccountService(db).resolve(user,request_id,data)
