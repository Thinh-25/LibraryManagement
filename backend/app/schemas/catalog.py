from datetime import date
from typing import Annotated, Literal
import re
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, field_validator, model_validator

Name100 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


def validate_cover(value):
    if value is None:
        return None
    if isinstance(value, str) and re.fullmatch(r'/media/covers/[0-9a-f]{32}\.webp', value):
        return value
    if isinstance(value, str):
        return str(HttpUrl(value))
    raise ValueError('Ảnh bìa phải là URL ảnh hợp lệ.')

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class CategoryCreate(Input):
    ten_the_loai: Name100
    mo_ta: str | None = Field(None, max_length=500)
class CategoryPatch(Input):
    ten_the_loai: Name100 | None = None
    mo_ta: str | None = Field(None, max_length=500)
class AuthorCreate(Input):
    ho_ten: Name100
    tieu_su: str | None = None
class AuthorPatch(Input):
    ho_ten: Name100 | None = None
    tieu_su: str | None = None
class PublisherCreate(Input):
    ten_nxb: str = Field(min_length=1, max_length=150)
    dia_chi: str | None = Field(None, max_length=255)
    so_dien_thoai: str | None = Field(None, pattern=r'^[0-9+]{9,15}$')
class PublisherPatch(Input):
    ten_nxb: str | None = Field(None, min_length=1, max_length=150)
    dia_chi: str | None = Field(None, max_length=255)
    so_dien_thoai: str | None = Field(None, pattern=r'^[0-9+]{9,15}$')
class BookCreate(Input):
    isbn: str | None = Field(None, min_length=1, max_length=20)
    ten_sach: str = Field(min_length=1, max_length=255)
    the_loai_id: int = Field(gt=0)
    nha_xuat_ban_id: int = Field(gt=0)
    nam_xuat_ban: int | None = Field(None, ge=1450, le=2200)
    mo_ta: str | None = None
    anh_bia: str | None = Field(None, max_length=500)
    author_ids: list[Annotated[int, Field(gt=0)]] = Field(default_factory=list)
    _cover = field_validator('anh_bia', mode='before')(validate_cover)
    @field_validator('author_ids')
    @classmethod
    def unique_authors(cls, value):
        if len(value) != len(set(value)):
            raise ValueError('Tác giả bị trùng.')
        return value
class BookPatch(Input):
    isbn: str | None = Field(None, min_length=1, max_length=20)
    ten_sach: str | None = Field(None, min_length=1, max_length=255)
    the_loai_id: int | None = Field(None, gt=0)
    nha_xuat_ban_id: int | None = Field(None, gt=0)
    nam_xuat_ban: int | None = Field(None, ge=1450, le=2200)
    mo_ta: str | None = None
    anh_bia: str | None = Field(None, max_length=500)
    author_ids: list[Annotated[int, Field(gt=0)]] | None = None
    _cover = field_validator('anh_bia', mode='before')(validate_cover)
    @field_validator('author_ids')
    @classmethod
    def unique_authors(cls, value):
        return BookCreate.unique_authors(value) if value is not None else value
class CopyCreate(Input):
    ma_vach: str = Field(min_length=1, max_length=50)
    vi_tri_ke: str | None = Field(None, max_length=100)
    tinh_trang: Literal['AVAILABLE', 'DAMAGED', 'LOST'] = 'AVAILABLE'
class CopyPatch(Input):
    ma_vach: str | None = Field(None, min_length=1, max_length=50)
    vi_tri_ke: str | None = Field(None, max_length=100)
    tinh_trang: Literal['AVAILABLE', 'DAMAGED', 'LOST'] | None = None
class CardCreate(Input):
    ma_the: str = Field(min_length=1, max_length=20)
    ngay_cap: date
    ngay_het_han: date
    @model_validator(mode='after')
    def valid_dates(self):
        if self.ngay_het_han <= self.ngay_cap:
            raise ValueError('Ngày hết hạn phải sau ngày cấp.')
        return self
class CardPatch(Input):
    ngay_het_han: date | None = None
    trang_thai: Literal['ACTIVE', 'EXPIRED', 'BLOCKED'] | None = None
