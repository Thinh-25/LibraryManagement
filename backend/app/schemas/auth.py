from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

Role = Literal['ADMIN','THU_THU','DOC_GIA']

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid')

    @field_validator('ho_ten', mode='before', check_fields=False)
    @classmethod
    def trim_name(cls, value):
        return value.strip() if isinstance(value, str) else value

class EmailInput(Input):
    email: str = Field(min_length=3, max_length=150, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    @field_validator('email', mode='before')
    @classmethod
    def normalize(cls, v):
        return v.strip().lower() if isinstance(v, str) else v

class Login(EmailInput):
    password: str = Field(min_length=1, max_length=256)

class ProfileUpdate(Input):
    ho_ten: str | None = Field(default=None, min_length=1, max_length=100)
    so_dien_thoai: str | None = Field(default=None, pattern=r'^[0-9+]{9,15}$')

class UserCreate(EmailInput):
    ho_ten: str = Field(min_length=1,max_length=100)
    so_dien_thoai: str | None = Field(default=None,pattern=r'^[0-9+]{9,15}$')
    vai_tro: Literal['THU_THU','DOC_GIA']
    password: str = Field(min_length=12,max_length=256)

class UserUpdate(ProfileUpdate):
    email: str | None = Field(default=None,max_length=150,pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    vai_tro: Role | None = None
    trang_thai: bool | None = None
    @field_validator('email', mode='before')
    @classmethod
    def normalize(cls,v):
        return v.strip().lower() if isinstance(v, str) else v

class PasswordChange(Input):
    current_password: str = Field(min_length=1,max_length=256)
    new_password: str = Field(min_length=12,max_length=256)

class PasswordReset(Input):
    new_password: str = Field(min_length=12,max_length=256)

class ResolveRequest(Input):
    new_password: str | None = Field(default=None,min_length=12,max_length=256)
    reject: bool = False

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ho_ten: str
    email: str
    so_dien_thoai: str | None
    vai_tro: Role
    trang_thai: bool
    ngay_tao: datetime
    must_change_password: bool
