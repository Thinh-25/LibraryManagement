from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LoanSelection(Input):
    cuon_sach_id: int = Field(gt=0)
    han_tra: AwareDatetime


class BorrowInput(Input):
    doc_gia_id: int = Field(gt=0)
    ghi_chu: str | None = Field(default=None, max_length=500)
    items: list[LoanSelection] = Field(min_length=1, max_length=100)
    reservation_id: int | None = Field(default=None, gt=0)


class ReturnInput(Input):
    condition: Literal["GOOD", "DAMAGED", "LOST"]
    note: str | None = Field(default=None, max_length=100)
    fine_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    fine_reason: str | None = Field(default=None, min_length=1, max_length=255)


class ReservationInput(Input):
    sach_id: int = Field(gt=0)


class FineInput(Input):
    chi_tiet_muon_id: int = Field(gt=0)
    ly_do: str = Field(min_length=1, max_length=255)
    so_tien: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
