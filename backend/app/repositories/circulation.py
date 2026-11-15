from datetime import datetime, UTC
from sqlalchemy import select, func, update
from app.core.errors import BusinessError
from app.models.entities import User, Book, BookCopy, Borrowing, LoanItem, Reservation, Fine


def record(item):
    return {column.key: getattr(item, column.key) for column in item.__table__.columns}


class CirculationRepository:
    def __init__(self, db):
        self.db = db

    def many(self, model, *conditions, order=(), lock=False):
        query = select(model).where(*conditions).order_by(*order)
        if lock:
            query = query.with_for_update().execution_options(populate_existing=True)
        return list(self.db.scalars(query))

    def find(self, model, *conditions, lock=False, required=True):
        rows = self.many(model, *conditions, lock=lock)
        if not rows:
            if required:
                raise BusinessError(404, "Không tìm thấy dữ liệu.")
            return None
        return rows[0]

    def get(self, model, item_id, lock=False):
        return self.find(model, model.id == item_id, lock=lock)

    def count(self, model, *conditions):
        return self.db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    def expire_reservations(self, now, book_id=None):
        conditions = [Reservation.trang_thai == "READY", Reservation.ngay_het_han <= now]
        if book_id is not None:
            conditions.append(Reservation.sach_id == book_id)
        self.db.execute(update(Reservation).where(*conditions).values(trang_thai="CANCELLED"),
                        execution_options={"synchronize_session": "fetch"})

    def page(self, query, page, size, serialize):
        total = self.db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
        rows = self.db.scalars(query.offset((page-1)*size).limit(size))
        return {"items": [serialize(row) for row in rows], "total": total, "page": page, "page_size": size}

    def loan_data(self, item):
        copy = self.db.get(BookCopy, item.cuon_sach_id)
        return {**record(item), "ten_sach": self.db.get(Book, copy.sach_id).ten_sach, "ma_vach": copy.ma_vach}

    def borrowing_data(self, row, status=None):
        result = {**record(row), "doc_gia_name": self.db.get(User, row.doc_gia_id).ho_ten,
                  "thu_thu_name": self.db.get(User, row.thu_thu_id).ho_ten}
        items = self.many(LoanItem, LoanItem.phieu_muon_id == row.id, order=(LoanItem.id,))
        if status == "borrowed":
            items = [i for i in items if i.trang_thai == "BORROWED"]
        elif status == "overdue":
            items = [i for i in items if i.trang_thai == "BORROWED" and i.han_tra < datetime.now(UTC)]
        elif status == "history":
            items = [i for i in items if i.trang_thai != "BORROWED"]
        result["items"] = [self.loan_data(i) for i in items]
        return result

    def list_borrowings(self, page, size, reader_id=None, status=None):
        query = select(Borrowing)
        if reader_id is not None:
            query = query.where(Borrowing.doc_gia_id == reader_id)
        conditions = [LoanItem.phieu_muon_id == Borrowing.id]
        if status == "borrowed":
            conditions.append(LoanItem.trang_thai == "BORROWED")
        elif status == "overdue":
            conditions += [LoanItem.trang_thai == "BORROWED", LoanItem.han_tra < datetime.now(UTC)]
        elif status == "history":
            conditions.append(LoanItem.trang_thai != "BORROWED")
        if status:
            query = query.where(select(LoanItem.id).where(*conditions).exists())
        return self.page(query.order_by(Borrowing.ngay_muon.desc(), Borrowing.id.desc()), page, size, lambda row: self.borrowing_data(row, status))

    def reservation_data(self, row):
        return {**record(row), "doc_gia_name": self.db.get(User, row.doc_gia_id).ho_ten,
                "ten_sach": self.db.get(Book, row.sach_id).ten_sach}

    def list_reservations(self, page, size, reader_id=None, status=None):
        query = select(Reservation)
        if reader_id is not None:
            query = query.where(Reservation.doc_gia_id == reader_id)
        if status:
            query = query.where(Reservation.trang_thai == status)
        return self.page(query.order_by(Reservation.ngay_dat.desc(), Reservation.id.desc()), page, size, self.reservation_data)

    def fine_data(self, row):
        detail = self.db.get(LoanItem, row.chi_tiet_muon_id)
        loan = self.db.get(Borrowing, detail.phieu_muon_id)
        copy = self.db.get(BookCopy, detail.cuon_sach_id)
        return {**record(row), "doc_gia_id": loan.doc_gia_id, "doc_gia_name": self.db.get(User, loan.doc_gia_id).ho_ten,
                "ten_sach": self.db.get(Book, copy.sach_id).ten_sach}

    def list_fines(self, page, size, reader_id=None, status=None):
        query = select(Fine)
        if reader_id is not None:
            query = query.join(LoanItem, Fine.chi_tiet_muon_id == LoanItem.id).join(Borrowing, LoanItem.phieu_muon_id == Borrowing.id).where(Borrowing.doc_gia_id == reader_id)
        if status:
            query = query.where(Fine.trang_thai == status)
        return self.page(query.order_by(Fine.ngay_tao.desc(), Fine.id.desc()), page, size, self.fine_data)

    def reports(self, start, end):
        def bounds(column):
            return ([column >= start] if start else []) + ([column < end] if end else [])
        now = datetime.now(UTC)
        summary = {"books": self.count(Book), "copies": self.count(BookCopy),
                   "readers": self.count(User, User.vai_tro == "DOC_GIA"),
                   "active_readers": self.count(User, User.vai_tro == "DOC_GIA", User.trang_thai.is_(True)),
                   "borrowed": self.count(LoanItem, LoanItem.trang_thai == "BORROWED"),
                   "overdue": self.count(LoanItem, LoanItem.trang_thai == "BORROWED", LoanItem.han_tra < now)}
        for key, state, column in [("paid_fines", "PAID", Fine.ngay_thanh_toan), ("unpaid_fines", "UNPAID", Fine.ngay_tao)]:
            summary[key] = str(self.db.scalar(select(func.coalesce(func.sum(Fine.so_tien), 0)).where(Fine.trang_thai == state, *bounds(column))))
        month = func.to_char(func.timezone("Asia/Ho_Chi_Minh", Borrowing.ngay_muon), "YYYY-MM")
        monthly = self.db.execute(select(month.label("month"), func.count(LoanItem.id).label("count")).join(LoanItem, LoanItem.phieu_muon_id == Borrowing.id).where(*bounds(Borrowing.ngay_muon)).group_by(month).order_by(month)).mappings().all()
        popular = self.db.execute(select(Book.id, Book.ten_sach, func.count(LoanItem.id).label("count")).join(BookCopy, BookCopy.sach_id == Book.id).join(LoanItem, LoanItem.cuon_sach_id == BookCopy.id).join(Borrowing, Borrowing.id == LoanItem.phieu_muon_id).where(*bounds(Borrowing.ngay_muon)).group_by(Book.id).order_by(func.count(LoanItem.id).desc(), Book.id).limit(10)).mappings().all()
        return {"summary": summary, "monthly": [dict(row) for row in monthly], "popular": [dict(row) for row in popular]}
