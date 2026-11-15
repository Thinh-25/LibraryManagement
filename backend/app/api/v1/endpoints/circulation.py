from datetime import date
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.auth import require_roles
from app.dependencies.database import get_db
from app.models.entities import User
from app.schemas.circulation import BorrowInput, ReturnInput, ReservationInput, FineInput
from app.services.circulation import CirculationService

router = APIRouter(tags=["Mượn trả, đặt trước, tiền phạt và báo cáo"])
DB = Annotated[Session, Depends(get_db)]
Staff = Annotated[User, Depends(require_roles("ADMIN", "THU_THU"))]
Reader = Annotated[User, Depends(require_roles("DOC_GIA"))]
AnyUser = Annotated[User, Depends(require_roles("ADMIN", "THU_THU", "DOC_GIA"))]
Page = Annotated[int, Query(ge=1)]
Size = Annotated[int, Query(ge=1, le=100)]


@router.get("/borrowings")
def borrowings(db: DB, user: Staff, page: Page = 1, page_size: Size = 20, reader_id: int | None = None):
    return CirculationService(db).repo.list_borrowings(page, page_size, reader_id)


@router.get("/my-borrowings")
def personal_borrowings(db: DB, user: Reader, page: Page = 1, page_size: Size = 20, status: Literal["borrowed", "overdue", "history"] | None = None):
    return CirculationService(db).repo.list_borrowings(page, page_size, user.id, status)


@router.get("/borrowings/{borrowing_id}")
def borrowing(borrowing_id: int, db: DB, user: AnyUser):
    return CirculationService(db).detail(borrowing_id, user)


@router.post("/borrowings", status_code=201)
def checkout(body: BorrowInput, db: DB, user: Staff):
    return CirculationService(db).borrow(body, user)


@router.post("/loan-items/{item_id}/return")
def return_item(item_id: int, body: ReturnInput, db: DB, user: Staff):
    return CirculationService(db).return_item(item_id, body)


@router.get("/reservations")
def reservations(db: DB, user: Staff, page: Page = 1, page_size: Size = 20, status: Literal["PENDING", "READY", "COMPLETED", "CANCELLED"] | None = None):
    return CirculationService(db).reservations(page, page_size, status=status)


@router.get("/my-reservations")
def personal_reservations(db: DB, user: Reader, page: Page = 1, page_size: Size = 20, status: Literal["PENDING", "READY", "COMPLETED", "CANCELLED"] | None = None):
    return CirculationService(db).reservations(page, page_size, user.id, status)


@router.post("/reservations", status_code=201)
def reserve(body: ReservationInput, db: DB, user: Reader):
    return CirculationService(db).reserve(body.sach_id, user)


@router.post("/reservations/{reservation_id}/ready")
def ready(reservation_id: int, db: DB, user: Staff):
    return CirculationService(db).ready(reservation_id)


@router.post("/reservations/{reservation_id}/cancel")
def cancel(reservation_id: int, db: DB, user: AnyUser):
    return CirculationService(db).cancel(reservation_id, user)


@router.get("/fines")
def fines(db: DB, user: Staff, page: Page = 1, page_size: Size = 20, status: Literal["UNPAID", "PAID"] | None = None):
    return CirculationService(db).repo.list_fines(page, page_size, status=status)


@router.get("/my-fines")
def personal_fines(db: DB, user: Reader, page: Page = 1, page_size: Size = 20, status: Literal["UNPAID", "PAID"] | None = None):
    return CirculationService(db).repo.list_fines(page, page_size, user.id, status)


@router.post("/fines", status_code=201)
def create_fine(body: FineInput, db: DB, user: Staff):
    return CirculationService(db).create_fine(body)


@router.post("/fines/{fine_id}/pay")
def pay(fine_id: int, db: DB, user: Staff):
    return CirculationService(db).pay(fine_id)


@router.get("/reports")
def reports(db: DB, user: Staff, start_date: date | None = None, end_date: date | None = None):
    return CirculationService(db).reports(start_date, end_date)
