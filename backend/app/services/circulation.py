from datetime import datetime, timedelta, UTC
from functools import wraps
from zoneinfo import ZoneInfo
from app.core.config import get_settings
from app.core.errors import BusinessError
from app.models.entities import User, LibraryCard, Book, BookCopy, Borrowing, LoanItem, Reservation, Fine
from app.repositories.circulation import CirculationRepository

VIETNAM = ZoneInfo("Asia/Ho_Chi_Minh")


def transactional(method):
    @wraps(method)
    def execute(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise
    return execute


class CirculationService:
    def __init__(self, db):
        self.db = db
        self.repo = CirculationRepository(db)

    def _expire(self, book_id=None):
        self.repo.expire_reservations(datetime.now(UTC), book_id)

    def _lock_book(self, book_id):
        return self.repo.get(Book, book_id, lock=True)

    def _queue(self, book_id):
        self._expire(book_id)
        return self.repo.many(Reservation, Reservation.sach_id == book_id, Reservation.trang_thai.in_(["PENDING", "READY"]), order=(Reservation.ngay_dat, Reservation.id))

    @transactional
    def borrow(self, body, staff):
        now = datetime.now(UTC)
        ids = [item.cuon_sach_id for item in body.items]
        if len(set(ids)) != len(ids):
            raise BusinessError(422, "Không chọn một cuốn sách nhiều lần trong phiếu.")
        if any(item.han_tra <= now for item in body.items):
            raise BusinessError(422, "Hạn trả phải ở tương lai.")
        reader = self.repo.get(User, body.doc_gia_id, lock=True)
        if reader.vai_tro != "DOC_GIA" or not reader.trang_thai:
            raise BusinessError(409, "Tài khoản độc giả không hợp lệ hoặc đã bị khóa.")
        card = self.repo.find(LibraryCard, LibraryCard.nguoi_dung_id == reader.id, lock=True, required=False)
        today = now.astimezone(VIETNAM).date()
        if card is None or card.trang_thai != "ACTIVE" or card.ngay_cap > today or card.ngay_het_han < today:
            raise BusinessError(409, "Độc giả chưa có thẻ hợp lệ hoặc thẻ đã hết hạn/bị khóa.")
        copies = self.repo.many(BookCopy, BookCopy.id.in_(ids), order=(BookCopy.id,))
        if len(copies) != len(ids):
            raise BusinessError(404, "Một hoặc nhiều cuốn sách không tồn tại.")
        for book_id in sorted({copy.sach_id for copy in copies}):
            self._lock_book(book_id)
        copies = self.repo.many(BookCopy, BookCopy.id.in_(ids), order=(BookCopy.id,), lock=True)
        for copy in copies:
            if copy.tinh_trang != "AVAILABLE" or self.repo.count(LoanItem, LoanItem.cuon_sach_id == copy.id, LoanItem.trang_thai == "BORROWED"):
                raise BusinessError(409, "Cuốn sách không còn sẵn sàng để mượn.")
        reservation = None
        if body.reservation_id is not None:
            reservation = self.repo.get(Reservation, body.reservation_id, lock=True)
            self._expire(reservation.sach_id)
            if reservation.doc_gia_id != reader.id or reservation.sach_id not in {copy.sach_id for copy in copies} or reservation.trang_thai != "READY":
                raise BusinessError(409, "Yêu cầu đặt trước không phù hợp hoặc không còn sẵn sàng.")
        loan = Borrowing(doc_gia_id=reader.id, thu_thu_id=staff.id, ghi_chu=body.ghi_chu, ngay_muon=now)
        self.db.add(loan); self.db.flush()
        deadlines = {item.cuon_sach_id: item.han_tra for item in body.items}
        for copy in copies:
            self.db.add(LoanItem(phieu_muon_id=loan.id, cuon_sach_id=copy.id, han_tra=deadlines[copy.id], trang_thai="BORROWED"))
            copy.tinh_trang = "BORROWED"
        if reservation is not None:
            reservation.trang_thai = "COMPLETED"
        self.db.flush()
        return self.repo.borrowing_data(loan)

    @transactional
    def return_item(self, item_id, body):
        item = self.repo.get(LoanItem, item_id, lock=True)
        copy = self.repo.get(BookCopy, item.cuon_sach_id, lock=True)
        if item.trang_thai != "BORROWED":
            raise BusinessError(409, "Lượt mượn này đã được xử lý trả/mất.")
        if body.fine_amount is not None and not body.fine_reason:
            raise BusinessError(422, "Vui lòng nhập lý do khoản phạt.")
        item.trang_thai = "LOST" if body.condition == "LOST" else "RETURNED"
        item.ngay_tra = None if body.condition == "LOST" else datetime.now(UTC)
        item.tinh_trang_khi_tra = body.note or {"GOOD":"Bình thường", "DAMAGED":"Hỏng", "LOST":"Mất"}[body.condition]
        copy.tinh_trang = "AVAILABLE" if body.condition == "GOOD" else body.condition
        if body.fine_amount is not None:
            self.db.add(Fine(chi_tiet_muon_id=item.id, so_tien=body.fine_amount, ly_do=body.fine_reason, trang_thai="UNPAID"))
        self.db.flush()
        return self.repo.loan_data(item)

    def detail(self, loan_id, user):
        row = self.repo.get(Borrowing, loan_id)
        if user.vai_tro == "DOC_GIA" and row.doc_gia_id != user.id:
            raise BusinessError(404, "Không tìm thấy phiếu mượn.")
        return self.repo.borrowing_data(row)

    @transactional
    def reserve(self, book_id, user):
        self._lock_book(book_id)
        self._expire(book_id)
        if self.repo.count(Reservation, Reservation.doc_gia_id == user.id, Reservation.sach_id == book_id, Reservation.trang_thai.in_(["PENDING", "READY"])):
            raise BusinessError(409, "Bạn đã có yêu cầu đặt trước đang hoạt động cho sách này.")
        row = Reservation(doc_gia_id=user.id, sach_id=book_id, trang_thai="PENDING", ngay_dat=datetime.now(UTC))
        self.db.add(row); self.db.flush()
        return self.repo.reservation_data(row)

    @transactional
    def ready(self, reservation_id):
        row = self.repo.get(Reservation, reservation_id)
        self._lock_book(row.sach_id)
        queue = self._queue(row.sach_id)
        row = self.repo.get(Reservation, reservation_id, lock=True)
        if row.trang_thai != "PENDING" or not queue or queue[0].id != row.id:
            raise BusinessError(409, "Chỉ yêu cầu đầu hàng đợi được xác nhận sẵn sàng.")
        if not self.repo.count(BookCopy, BookCopy.sach_id == row.sach_id, BookCopy.tinh_trang == "AVAILABLE"):
            raise BusinessError(409, "Chưa có bản sao sẵn sàng.")
        row.trang_thai = "READY"
        row.ngay_het_han = datetime.now(UTC) + timedelta(hours=get_settings().reservation_hold_hours)
        self.db.flush()
        return self.repo.reservation_data(row)

    @transactional
    def cancel(self, reservation_id, user):
        row = self.repo.get(Reservation, reservation_id)
        if user.vai_tro == "DOC_GIA" and row.doc_gia_id != user.id:
            raise BusinessError(404, "Không tìm thấy yêu cầu đặt trước.")
        self._lock_book(row.sach_id)
        row = self.repo.get(Reservation, reservation_id, lock=True)
        if row.trang_thai not in {"PENDING", "READY"}:
            raise BusinessError(409, "Yêu cầu không thể hủy ở trạng thái hiện tại.")
        row.trang_thai = "CANCELLED"
        self.db.flush()
        return self.repo.reservation_data(row)

    @transactional
    def reservations(self, page, size, reader_id=None, status=None):
        self._expire()
        return self.repo.list_reservations(page, size, reader_id, status)

    @transactional
    def create_fine(self, body):
        self.repo.get(LoanItem, body.chi_tiet_muon_id)
        row = Fine(**body.model_dump(), trang_thai="UNPAID")
        self.db.add(row); self.db.flush()
        return self.repo.fine_data(row)

    @transactional
    def pay(self, fine_id):
        row = self.repo.get(Fine, fine_id, lock=True)
        if row.trang_thai != "UNPAID":
            raise BusinessError(409, "Khoản phạt đã được thanh toán.")
        row.trang_thai = "PAID"
        row.ngay_thanh_toan = datetime.now(UTC)
        self.db.flush()
        return self.repo.fine_data(row)

    def reports(self, start_date, end_date):
        if start_date and end_date and start_date > end_date:
            raise BusinessError(422, "Ngày bắt đầu phải không sau ngày kết thúc.")
        if (start_date and not 1900 <= start_date.year <= 2200) or (end_date and not 1900 <= end_date.year <= 2200):
            raise BusinessError(422, "Khoảng báo cáo phải nằm trong các năm 1900–2200.")
        start = datetime.combine(start_date, datetime.min.time(), VIETNAM).astimezone(UTC) if start_date else None
        end = datetime.combine(end_date+timedelta(days=1), datetime.min.time(), VIETNAM).astimezone(UTC) if end_date else None
        return self.repo.reports(start, end)
