from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, Integer, Identity, Numeric, String, Text, text
from app.db.base import Base


def pk():
    return Column(BigInteger, Identity(), primary_key=True)


def fk(target, **kw):
    return Column(BigInteger, ForeignKey(target, ondelete=kw.pop('ondelete', 'RESTRICT')), **kw)


def timestamp():
    return Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))


class User(Base):
    __tablename__ = 'nguoi_dung'
    id = pk()
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    mat_khau_hash = Column(String(255), nullable=False)
    so_dien_thoai = Column(String(15))
    vai_tro = Column(String(20), nullable=False)
    trang_thai = Column(Boolean, nullable=False, server_default=text('true'), default=True)
    ngay_tao = timestamp()
    auth_version = Column(Integer, nullable=False, default=0, server_default=text('0'))
    must_change_password = Column(Boolean, nullable=False, default=False, server_default=text('false'))

class LibraryCard(Base):
    __tablename__ = 'the_thu_vien'
    id = pk()
    nguoi_dung_id = fk('nguoi_dung.id', nullable=False, unique=True)
    ma_the = Column(String(20), nullable=False, unique=True)
    ngay_cap = Column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    ngay_het_han = Column(Date, nullable=False)
    trang_thai = Column(String(20), nullable=False, server_default='ACTIVE')

class Category(Base):
    __tablename__ = 'the_loai'
    id = pk()
    ten_the_loai = Column(String(100), nullable=False, unique=True)
    mo_ta = Column(String(500))

class Author(Base):
    __tablename__ = 'tac_gia'
    id = pk()
    ho_ten = Column(String(100), nullable=False)
    tieu_su = Column(Text)

class Publisher(Base):
    __tablename__ = 'nha_xuat_ban'
    id = pk()
    ten_nxb = Column(String(150), nullable=False, unique=True)
    dia_chi = Column(String(255))
    so_dien_thoai = Column(String(15))

class Book(Base):
    __tablename__ = 'sach'
    id = pk()
    isbn = Column(String(20), unique=True)
    ten_sach = Column(String(255), nullable=False)
    the_loai_id = fk('the_loai.id', nullable=False)
    nha_xuat_ban_id = fk('nha_xuat_ban.id', nullable=False)
    nam_xuat_ban = Column(Integer)
    mo_ta = Column(Text)
    anh_bia = Column(String(500))
    ngay_tao = timestamp()

class BookAuthor(Base):
    __tablename__ = 'sach_tac_gia'
    sach_id = fk('sach.id', primary_key=True, ondelete='CASCADE')
    tac_gia_id = fk('tac_gia.id', primary_key=True)

class BookCopy(Base):
    __tablename__ = 'cuon_sach'
    id = pk()
    sach_id = fk('sach.id', nullable=False)
    ma_vach = Column(String(50), nullable=False, unique=True)
    vi_tri_ke = Column(String(100))
    tinh_trang = Column(String(20), nullable=False, server_default='AVAILABLE')

class Borrowing(Base):
    __tablename__ = 'phieu_muon'
    id = pk()
    doc_gia_id = fk('nguoi_dung.id', nullable=False)
    thu_thu_id = fk('nguoi_dung.id', nullable=False)
    ngay_muon = timestamp()
    ghi_chu = Column(String(500))

class LoanItem(Base):
    __tablename__ = 'chi_tiet_muon'
    id = pk()
    phieu_muon_id = fk('phieu_muon.id', nullable=False)
    cuon_sach_id = fk('cuon_sach.id', nullable=False)
    han_tra = Column(DateTime(timezone=True), nullable=False)
    ngay_tra = Column(DateTime(timezone=True))
    trang_thai = Column(String(20), nullable=False, server_default='BORROWED')
    tinh_trang_khi_tra = Column(String(100))

class Reservation(Base):
    __tablename__ = 'dat_truoc_sach'
    id = pk()
    doc_gia_id = fk('nguoi_dung.id', nullable=False)
    sach_id = fk('sach.id', nullable=False)
    ngay_dat = timestamp()
    ngay_het_han = Column(DateTime(timezone=True))
    trang_thai = Column(String(20), nullable=False, server_default='PENDING')

class Fine(Base):
    __tablename__ = 'tien_phat'
    id = pk()
    chi_tiet_muon_id = fk('chi_tiet_muon.id', nullable=False)
    ly_do = Column(String(255), nullable=False)
    so_tien = Column(Numeric(12,2), nullable=False)
    trang_thai = Column(String(20), nullable=False, server_default='UNPAID')
    ngay_tao = timestamp()
    ngay_thanh_toan = Column(DateTime(timezone=True))

class PasswordResetRequest(Base):
    __tablename__ = 'password_reset_request'
    id = pk()
    nguoi_dung_id = fk('nguoi_dung.id', nullable=False)
    trang_thai = Column(String(20), nullable=False, server_default='PENDING')
    ngay_tao = timestamp()
    ngay_xu_ly = Column(DateTime(timezone=True))
    admin_id = fk('nguoi_dung.id')

# Mirror the baseline constraints and indexes so Alembic sees the complete schema.
from sqlalchemy import CheckConstraint, Index, func
from sqlalchemy.schema import conv

_checks = {
    User: [('nguoi_dung_ho_ten_check', "btrim(ho_ten) <> ''"), ('nguoi_dung_vai_tro_check', "vai_tro IN ('ADMIN','THU_THU','DOC_GIA')"), ('ck_email_format', "email ~* '^[^[:space:]@]+@[^[:space:]@]+\\.[^[:space:]@]+$'"), ('ck_sdt', "so_dien_thoai IS NULL OR so_dien_thoai ~ '^[0-9+]{9,15}$'")],
    LibraryCard: [('the_thu_vien_trang_thai_check', "trang_thai IN ('ACTIVE','EXPIRED','BLOCKED')"), ('ck_han_the', 'ngay_het_han > ngay_cap')],
    Book: [('sach_ten_sach_check', "btrim(ten_sach) <> ''"), ('sach_nam_xuat_ban_check', 'nam_xuat_ban BETWEEN 1450 AND 2200')],
    BookCopy: [('cuon_sach_tinh_trang_check', "tinh_trang IN ('AVAILABLE','BORROWED','DAMAGED','LOST')")],
    LoanItem: [('chi_tiet_muon_trang_thai_check', "trang_thai IN ('BORROWED','RETURNED','LOST')"), ('ck_chi_tiet_tra', "(trang_thai = 'RETURNED' AND ngay_tra IS NOT NULL) OR (trang_thai IN ('BORROWED','LOST') AND ngay_tra IS NULL)")],
    Reservation: [('dat_truoc_sach_trang_thai_check', "trang_thai IN ('PENDING','READY','COMPLETED','CANCELLED')"), ('ck_dat_truoc_han', 'ngay_het_han IS NULL OR ngay_het_han > ngay_dat')],
    Fine: [('tien_phat_so_tien_check', 'so_tien > 0'), ('tien_phat_trang_thai_check', "trang_thai IN ('UNPAID','PAID')"), ('ck_tien_phat_paid', "(trang_thai = 'PAID' AND ngay_thanh_toan IS NOT NULL AND ngay_thanh_toan >= ngay_tao) OR (trang_thai = 'UNPAID' AND ngay_thanh_toan IS NULL)")],
    PasswordResetRequest: [('ck_password_reset_request_reset_status', "trang_thai IN ('PENDING','RESOLVED','REJECTED')")],
}
for _model, _constraints in _checks.items():
    for _name, _condition in _constraints:
        _model.__table__.append_constraint(CheckConstraint(_condition, name=conv(_name)))

Index('uq_nguoi_dung_email_ci', func.lower(User.email), unique=True)
Index('uq_cuon_dang_muon', LoanItem.cuon_sach_id, unique=True, postgresql_where=text("trang_thai = 'BORROWED'"))
Index('uq_dat_truoc_active', Reservation.doc_gia_id, Reservation.sach_id, unique=True, postgresql_where=text("trang_thai IN ('PENDING','READY')"))
Index('uq_pending_password_reset', PasswordResetRequest.nguoi_dung_id, unique=True, postgresql_where=text("trang_thai = 'PENDING'"))
for _name, _column in [
    ('idx_sach_ten',Book.ten_sach), ('idx_sach_the_loai',Book.the_loai_id), ('idx_sach_nxb',Book.nha_xuat_ban_id),
    ('idx_sach_tac_gia_tac_gia',BookAuthor.tac_gia_id), ('idx_cuon_sach_sach',BookCopy.sach_id),
    ('idx_phieu_muon_doc_gia',Borrowing.doc_gia_id), ('idx_phieu_muon_thu_thu',Borrowing.thu_thu_id),
    ('idx_chi_tiet_muon_phieu',LoanItem.phieu_muon_id), ('idx_dat_truoc_sach',Reservation.sach_id),
    ('idx_tien_phat_chi_tiet',Fine.chi_tiet_muon_id),
]:
    Index(_name,_column)
Index('idx_chi_tiet_muon_han',LoanItem.han_tra,postgresql_where=text("trang_thai='BORROWED'"))

from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint, ForeignKeyConstraint
for _table in Base.metadata.tables.values():
    if _table.name == 'password_reset_request':
        continue
    for _constraint in _table.constraints:
        if isinstance(_constraint, UniqueConstraint):
            _cols = '_'.join(column.name for column in _constraint.columns)
            _constraint.name = conv('uq_nguoi_dung_email' if _table.name == 'nguoi_dung' and _cols == 'email' else f'{_table.name}_{_cols}_key')
        elif isinstance(_constraint, PrimaryKeyConstraint):
            _constraint.name = conv(f'{_table.name}_pkey')
        elif isinstance(_constraint, ForeignKeyConstraint):
            _cols = '_'.join(column.name for column in _constraint.columns)
            _constraint.name = conv(f'{_table.name}_{_cols}_fkey')
