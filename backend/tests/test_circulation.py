from datetime import date, datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy import select, func

from app.models.entities import (
    User, LibraryCard, Category, Publisher, Book, BookCopy, LoanItem, Borrowing, Reservation, Fine,
)


@pytest.fixture
def inventory(db):
    key = uuid4().hex
    reader = User(ho_ten="Bạn đọc", email=key + "@test.example", mat_khau_hash="invalid", vai_tro="DOC_GIA", trang_thai=True)
    other = User(ho_ten="Bạn đọc khác", email="other" + key + "@test.example", mat_khau_hash="invalid", vai_tro="DOC_GIA", trang_thai=True)
    category = Category(ten_the_loai="Thể loại " + key)
    publisher = Publisher(ten_nxb="NXB " + key)
    db.add_all([reader, other, category, publisher]); db.flush()
    book = Book(ten_sach="Sách kiểm thử", the_loai_id=category.id, nha_xuat_ban_id=publisher.id)
    db.add(book); db.flush()
    copies = [BookCopy(sach_id=book.id, ma_vach=key + str(i), tinh_trang="AVAILABLE") for i in range(2)]
    card = LibraryCard(nguoi_dung_id=reader.id, ma_the=key[:20], ngay_cap=date.today()-timedelta(days=1), ngay_het_han=date.today()+timedelta(days=30), trang_thai="ACTIVE")
    db.add_all([*copies, card]); db.flush(); db.commit()
    return {"reader": reader, "other": other, "book": book, "copies": copies, "card": card}


def checkout(client, auth_headers, inventory, **extra):
    payload = {"doc_gia_id": inventory["reader"].id, "items": [
        {"cuon_sach_id": copy.id, "han_tra": (datetime.now(UTC)+timedelta(days=7)).isoformat()}
        for copy in inventory["copies"]
    ], **extra}
    return client.post("/api/v1/borrowings", json=payload, headers=auth_headers("THU_THU"))


def test_checkout_atomic_and_prevents_double_borrow(client, db, auth_headers, inventory):
    result = checkout(client, auth_headers, inventory)
    assert result.status_code == 201, result.text
    assert len(result.json()["items"]) == 2
    assert all(db.get(BookCopy, c.id).tinh_trang == "BORROWED" for c in inventory["copies"])
    duplicate = checkout(client, auth_headers, inventory)
    assert duplicate.status_code == 409
    assert db.scalar(select(func.count()).select_from(Borrowing).where(Borrowing.doc_gia_id == inventory["reader"].id)) == 1


def test_invalid_copy_rolls_back_entire_checkout(client, db, auth_headers, inventory):
    inventory["copies"][1].tinh_trang = "DAMAGED"; db.flush()
    response = checkout(client, auth_headers, inventory)
    assert response.status_code == 409
    assert db.get(BookCopy, inventory["copies"][0].id).tinh_trang == "AVAILABLE"
    assert db.scalar(select(func.count()).select_from(Borrowing).where(Borrowing.doc_gia_id == inventory["reader"].id)) == 0


def test_expired_card_rejected(client, db, auth_headers, inventory):
    inventory["card"].ngay_cap = date.today()-timedelta(days=30)
    inventory["card"].ngay_het_han = date.today()-timedelta(days=1); db.flush()
    assert checkout(client, auth_headers, inventory).status_code == 409


@pytest.mark.parametrize("condition,copy_status,loan_status", [("GOOD","AVAILABLE","RETURNED"),("DAMAGED","DAMAGED","RETURNED"),("LOST","LOST","LOST")])
def test_return_state_and_double_return(client, db, auth_headers, inventory, condition, copy_status, loan_status):
    loan = checkout(client, auth_headers, inventory).json()["items"][0]
    response = client.post(f'/api/v1/loan-items/{loan["id"]}/return', json={"condition": condition}, headers=auth_headers("THU_THU"))
    assert response.status_code == 200, response.text
    db.expire_all()
    assert db.get(BookCopy, loan["cuon_sach_id"]).tinh_trang == copy_status
    detail = db.get(LoanItem, loan["id"])
    assert detail.trang_thai == loan_status
    assert (detail.ngay_tra is None) == (condition == "LOST")
    assert client.post(f'/api/v1/loan-items/{loan["id"]}/return', json={"condition":"GOOD"}, headers=auth_headers("ADMIN")).status_code == 409


def test_reader_scope_and_staff_permissions(client, auth_headers, inventory):
    loan = checkout(client, auth_headers, inventory).json()
    own = auth_headers("DOC_GIA", inventory["reader"].id)
    other = auth_headers("DOC_GIA", inventory["other"].id)
    assert client.get("/api/v1/my-borrowings", headers=own).json()["total"] == 1
    assert client.get("/api/v1/my-borrowings", headers=other).json()["total"] == 0
    assert client.get(f'/api/v1/borrowings/{loan["id"]}', headers=other).status_code == 404
    assert client.get("/api/v1/reports", headers=own).status_code == 403
    assert client.post("/api/v1/borrowings", json={"doc_gia_id":inventory["reader"].id,"items":[]}, headers=own).status_code == 403


def test_fine_payment_once_and_personal_scope(client, db, auth_headers, inventory):
    loan = checkout(client, auth_headers, inventory).json()["items"][0]
    fine = client.post("/api/v1/fines", json={"chi_tiet_muon_id":loan["id"],"so_tien":"10000","ly_do":"Quá hạn"}, headers=auth_headers("THU_THU"))
    assert fine.status_code == 201, fine.text
    fine_id = fine.json()["id"]
    assert client.post(f"/api/v1/fines/{fine_id}/pay", headers=auth_headers()).status_code == 200
    assert client.post(f"/api/v1/fines/{fine_id}/pay", headers=auth_headers()).status_code == 409
    assert client.get("/api/v1/my-fines", headers=auth_headers("DOC_GIA",inventory["other"].id)).json()["total"] == 0
    assert client.get("/api/v1/my-fines", headers=auth_headers("DOC_GIA",inventory["reader"].id)).json()["total"] == 1


def test_reservation_fifo_and_owner_cancellation(client, auth_headers, inventory):
    first_headers = auth_headers("DOC_GIA", inventory["reader"].id)
    second_headers = auth_headers("DOC_GIA", inventory["other"].id)
    first = client.post("/api/v1/reservations", json={"sach_id":inventory["book"].id}, headers=first_headers)
    second = client.post("/api/v1/reservations", json={"sach_id":inventory["book"].id}, headers=second_headers)
    assert first.status_code == second.status_code == 201
    assert client.post("/api/v1/reservations", json={"sach_id":inventory["book"].id}, headers=first_headers).status_code == 409
    second_id = second.json()["id"]
    assert client.post(f"/api/v1/reservations/{second_id}/ready", headers=auth_headers()).status_code == 409
    first_id = first.json()["id"]
    assert client.post(f"/api/v1/reservations/{first_id}/cancel", headers=second_headers).status_code == 404
    assert client.post(f"/api/v1/reservations/{first_id}/ready", headers=auth_headers()).status_code == 200
    assert client.post(f"/api/v1/reservations/{first_id}/cancel", headers=first_headers).status_code == 200
    assert client.post(f"/api/v1/reservations/{second_id}/ready", headers=auth_headers()).status_code == 200


def test_ready_reservation_completed_with_checkout(client, db, auth_headers, inventory):
    headers = auth_headers("DOC_GIA", inventory["reader"].id)
    reservation = client.post("/api/v1/reservations", json={"sach_id":inventory["book"].id}, headers=headers).json()
    rid = reservation["id"]
    assert client.post(f"/api/v1/reservations/{rid}/ready", headers=auth_headers()).status_code == 200
    result = checkout(client, auth_headers, inventory, reservation_id=rid)
    assert result.status_code == 201, result.text
    db.expire_all()
    assert db.get(Reservation,rid).trang_thai == "COMPLETED"


def test_reports_filter_validation_and_summary(client, auth_headers):
    result = client.get("/api/v1/reports", headers=auth_headers())
    assert result.status_code == 200, result.text
    assert {"summary","monthly","popular"} <= result.json().keys()
    assert client.get("/api/v1/reports?start_date=2026-12-01&end_date=2026-01-01", headers=auth_headers()).status_code == 422
    assert client.get("/api/v1/reports?end_date=9999-12-31", headers=auth_headers()).status_code == 422


def test_expired_ready_releases_fifo_and_status_filter(client, db, auth_headers, inventory):
    first_headers = auth_headers("DOC_GIA", inventory["reader"].id)
    second_headers = auth_headers("DOC_GIA", inventory["other"].id)
    first = client.post("/api/v1/reservations", json={"sach_id":inventory["book"].id}, headers=first_headers).json()
    second = client.post("/api/v1/reservations", json={"sach_id":inventory["book"].id}, headers=second_headers).json()
    assert client.post(f'/api/v1/reservations/{first["id"]}/ready', headers=auth_headers()).status_code == 200
    row = db.get(Reservation, first["id"])
    row.ngay_dat = datetime.now(UTC)-timedelta(days=2)
    row.ngay_het_han = datetime.now(UTC)-timedelta(days=1)
    db.commit()
    assert client.post(f'/api/v1/reservations/{second["id"]}/ready', headers=auth_headers()).status_code == 200
    cancelled = client.get("/api/v1/my-reservations?status=CANCELLED", headers=first_headers).json()
    assert cancelled["total"] == 1
    assert cancelled["items"][0]["id"] == first["id"]


def test_reports_use_vietnam_day_boundaries_and_decimal_money(client, db, auth_headers, inventory):
    headers = auth_headers("THU_THU")
    staff_id = client.get("/api/v1/auth/me", headers=headers).json()["id"]
    dates = [datetime(2030,1,1,16,59,59,tzinfo=UTC), datetime(2030,1,1,17,0,0,tzinfo=UTC)]
    details = []
    for copy, when in zip(inventory["copies"], dates):
        loan = Borrowing(doc_gia_id=inventory["reader"].id, thu_thu_id=staff_id, ngay_muon=when)
        db.add(loan); db.flush()
        detail = LoanItem(phieu_muon_id=loan.id, cuon_sach_id=copy.id, han_tra=when+timedelta(days=7), ngay_tra=when, trang_thai="RETURNED")
        db.add(detail); db.flush(); details.append(detail)
    db.add(Fine(chi_tiet_muon_id=details[0].id, ly_do="Kiểm tra tiền", so_tien="10000.25", trang_thai="PAID", ngay_tao=dates[0], ngay_thanh_toan=dates[1]))
    db.commit()
    response = client.get("/api/v1/reports?start_date=2030-01-02&end_date=2030-01-02", headers=headers)
    assert response.status_code == 200
    assert response.json()["monthly"] == [{"month":"2030-01", "count":1}]
    assert response.json()["summary"]["paid_fines"] == "10000.25"
