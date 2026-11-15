"""Actual PostgreSQL races; rows committed here are deleted by their owned IDs only."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, UTC
from threading import Barrier, Event
from uuid import uuid4

import pytest
from sqlalchemy import delete, event, select, text
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.models import (User, LibraryCard, Category, Publisher, Book, BookCopy,
                        Borrowing, LoanItem, Reservation, Fine)
from app.schemas.circulation import BorrowInput, ReturnInput
from app.services.circulation import CirculationService


@pytest.fixture
def committed_inventory(test_engine):
    assert test_engine.url.database == 'library_management_test'
    key = uuid4().hex
    with Session(test_engine, expire_on_commit=False) as db:
        reader = User(ho_ten='Concurrent reader', email=key+'@test.example',
                      mat_khau_hash='invalid', vai_tro='DOC_GIA')
        staff = User(ho_ten='Concurrent staff', email='staff'+key+'@test.example',
                     mat_khau_hash='invalid', vai_tro='THU_THU')
        category = Category(ten_the_loai=key)
        publisher = Publisher(ten_nxb=key)
        db.add_all([reader, staff, category, publisher]); db.flush()
        book = Book(ten_sach='Concurrent book', the_loai_id=category.id,
                    nha_xuat_ban_id=publisher.id)
        db.add(book); db.flush()
        copy = BookCopy(sach_id=book.id, ma_vach=key, tinh_trang='AVAILABLE')
        card = LibraryCard(nguoi_dung_id=reader.id, ma_the=key[:20],
                           ngay_cap=date.today()-timedelta(days=1),
                           ngay_het_han=date.today()+timedelta(days=30), trang_thai='ACTIVE')
        db.add_all([copy, card]); db.commit()
        ids = dict(reader=reader.id, staff=staff.id, category=category.id,
                   publisher=publisher.id, book=book.id, copy=copy.id, card=card.id)
    try:
        yield ids
    finally:
        with Session(test_engine) as db:
            loans = select(Borrowing.id).where(Borrowing.doc_gia_id == ids['reader'])
            items = select(LoanItem.id).where(LoanItem.phieu_muon_id.in_(loans))
            db.execute(delete(Fine).where(Fine.chi_tiet_muon_id.in_(items)))
            db.execute(delete(LoanItem).where(LoanItem.phieu_muon_id.in_(loans)))
            db.execute(delete(Borrowing).where(Borrowing.doc_gia_id == ids['reader']))
            db.execute(delete(Reservation).where(Reservation.sach_id == ids['book']))
            db.execute(delete(LibraryCard).where(LibraryCard.id == ids['card']))
            db.execute(delete(BookCopy).where(BookCopy.id == ids['copy']))
            db.execute(delete(Book).where(Book.id == ids['book']))
            db.execute(delete(Category).where(Category.id == ids['category']))
            db.execute(delete(Publisher).where(Publisher.id == ids['publisher']))
            db.execute(delete(User).where(User.id.in_([ids['reader'], ids['staff']])))
            db.commit()


def borrow_one(db, ids):
    body = BorrowInput(doc_gia_id=ids['reader'], items=[{
        'cuon_sach_id': ids['copy'], 'han_tra': datetime.now(UTC)+timedelta(days=7)}])
    return CirculationService(db).borrow(body, db.get(User, ids['staff']))


def race(test_engine, operation):
    start = Barrier(2, timeout=10)

    def worker():
        with Session(test_engine, expire_on_commit=False) as db:
            db.execute(text("SET LOCAL lock_timeout = '5s'"))
            start.wait()
            try:
                operation(db)
                return 200
            except BusinessError as error:
                return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker) for _ in range(2)]
        return sorted(future.result(timeout=15) for future in futures)


def test_simultaneous_borrow_same_copy_only_one_commits(test_engine, committed_inventory):
    ids = committed_inventory
    assert race(test_engine, lambda db: borrow_one(db, ids)) == [200, 409]
    with Session(test_engine) as db:
        items = db.scalars(select(LoanItem).where(LoanItem.cuon_sach_id == ids['copy'])).all()
        assert len(items) == 1
        assert items[0].trang_thai == 'BORROWED'
        assert db.get(BookCopy, ids['copy']).tinh_trang == 'BORROWED'


def test_simultaneous_return_only_one_commits(test_engine, committed_inventory):
    ids = committed_inventory
    with Session(test_engine) as db:
        item_id = borrow_one(db, ids)['items'][0]['id']
    assert race(test_engine, lambda db: CirculationService(db).return_item(
        item_id, ReturnInput(condition='GOOD'))) == [200, 409]
    with Session(test_engine) as db:
        assert db.get(LoanItem, item_id).trang_thai == 'RETURNED'
        assert db.get(BookCopy, ids['copy']).tinh_trang == 'AVAILABLE'


def test_simultaneous_payment_only_one_commits(test_engine, committed_inventory):
    ids = committed_inventory
    with Session(test_engine) as db:
        item_id = borrow_one(db, ids)['items'][0]['id']
        fine = Fine(chi_tiet_muon_id=item_id, so_tien='10000.00', ly_do='Concurrency check', trang_thai='UNPAID')
        db.add(fine); db.flush(); fine_id = fine.id; db.commit()
    assert race(test_engine, lambda db: CirculationService(db).pay(fine_id)) == [200, 409]
    with Session(test_engine) as db:
        assert db.get(Fine, fine_id).trang_thai == 'PAID'
        assert db.get(Fine, fine_id).ngay_thanh_toan is not None


def test_expiration_cannot_overwrite_concurrent_completed_reservation(test_engine, committed_inventory):
    ids = committed_inventory
    with Session(test_engine) as db:
        row = Reservation(doc_gia_id=ids['reader'], sach_id=ids['book'],
                          ngay_dat=datetime.now(UTC)-timedelta(days=2),
                          ngay_het_han=datetime.now(UTC)-timedelta(days=1), trang_thai='READY')
        db.add(row); db.flush(); reservation_id = row.id; db.commit()

    update_reached = Event()
    completion_committed = Event()
    with Session(test_engine) as completing:
        row = completing.scalar(select(Reservation).where(Reservation.id == reservation_id).with_for_update())
        row.trang_thai = 'COMPLETED'
        completing.flush()

        def expire():
            with test_engine.connect() as connection:
                def before_update(conn, cursor, statement, parameters, context, executemany):
                    if statement.lstrip().upper().startswith('UPDATE DAT_TRUOC_SACH'):
                        update_reached.set()
                        assert completion_committed.wait(10), 'Completion commit did not arrive.'
                event.listen(connection, 'before_cursor_execute', before_update)
                try:
                    with Session(connection) as expiring:
                        CirculationService(expiring)._expire(ids['book'])
                        expiring.commit()
                finally:
                    event.remove(connection, 'before_cursor_execute', before_update)

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(expire)
            try:
                assert update_reached.wait(10), 'Expiration did not issue its UPDATE.'
                completing.commit()
            finally:
                completion_committed.set()
            future.result(timeout=15)

    with Session(test_engine) as db:
        assert db.get(Reservation, reservation_id).trang_thai == 'COMPLETED'
