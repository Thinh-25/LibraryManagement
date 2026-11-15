from datetime import date, timedelta


def test_reader_cannot_manage_catalog(client, auth_headers):
    response = client.post('/api/v1/categories', json={'ten_the_loai': 'Restricted'}, headers=auth_headers('DOC_GIA'))
    assert response.status_code == 403


def test_catalog_crud_filter_and_reference_protection(client, auth_headers):
    headers = auth_headers('THU_THU')
    category = client.post('/api/v1/categories', json={'ten_the_loai': 'Science'}, headers=headers)
    assert category.status_code == 201
    cid = category.json()['id']
    publisher = client.post('/api/v1/publishers', json={'ten_nxb': 'Press'}, headers=headers).json()
    author = client.post('/api/v1/authors', json={'ho_ten': 'Writer'}, headers=headers).json()
    book = client.post('/api/v1/books', json={'ten_sach': 'Physics', 'the_loai_id': cid, 'nha_xuat_ban_id': publisher['id'], 'author_ids': [author['id']]}, headers=headers)
    assert book.status_code == 201
    bid = book.json()['id']
    copy = client.post(f'/api/v1/books/{bid}/copies', json={'ma_vach': 'TEST-1'}, headers=headers)
    assert copy.status_code == 201
    listing = client.get('/api/v1/books', params={'search': 'Phys', 'author_id': author['id']}, headers=auth_headers('DOC_GIA')).json()
    assert listing['total'] == 1
    assert listing['items'][0]['available_copies'] == 1
    assert listing['items'][0]['authors'][0]['ho_ten'] == 'Writer'
    assert client.delete(f'/api/v1/categories/{cid}', headers=headers).status_code == 409
    assert client.delete(f'/api/v1/books/{bid}', headers=headers).status_code == 409
    assert client.patch(f"/api/v1/copies/{copy.json()['id']}", json={'tinh_trang': 'BORROWED'}, headers=headers).status_code == 422
    assert client.delete(f"/api/v1/copies/{copy.json()['id']}", headers=headers).status_code == 204
    assert client.delete(f'/api/v1/books/{bid}', headers=headers).status_code == 204
    assert client.delete(f'/api/v1/categories/{cid}', headers=headers).status_code == 204


def test_card_dates_reader_scope_and_extension(client, auth_headers, db):
    from app.models.entities import User
    reader = User(ho_ten='Card Reader', email='cardreader@example.test', mat_khau_hash='unused', vai_tro='DOC_GIA', trang_thai=True)
    db.add(reader)
    db.commit()
    headers = auth_headers('THU_THU')
    today = date.today()
    payload = {'ma_the': 'CARD-T', 'ngay_cap': str(today), 'ngay_het_han': str(today)}
    assert client.post(f'/api/v1/readers/{reader.id}/card', json=payload, headers=headers).status_code == 422
    payload['ngay_het_han'] = str(today + timedelta(days=30))
    created = client.post(f'/api/v1/readers/{reader.id}/card', json=payload, headers=headers)
    assert created.status_code == 201
    card_id = created.json()['id']
    assert client.post(f'/api/v1/readers/{reader.id}/card', json=payload, headers=headers).status_code == 409
    assert client.patch(f'/api/v1/cards/{card_id}', json={'ngay_het_han': str(today + timedelta(days=10))}, headers=headers).status_code == 422
    assert client.patch(f'/api/v1/cards/{card_id}', json={'ngay_het_han': str(today + timedelta(days=60))}, headers=headers).status_code == 200
    detail = client.get(f'/api/v1/readers/{reader.id}', headers=headers).json()
    assert detail['card']['id'] == card_id
    assert 'mat_khau_hash' not in detail

def test_borrowed_copy_is_immutable_and_reader_cannot_view_readers(client, auth_headers, db):
    from app.models.entities import Category, Publisher, Book, BookCopy
    category = Category(ten_the_loai='Borrowed category')
    publisher = Publisher(ten_nxb='Borrowed publisher')
    db.add_all([category, publisher])
    db.flush()
    book = Book(ten_sach='Borrowed book', the_loai_id=category.id, nha_xuat_ban_id=publisher.id)
    db.add(book)
    db.flush()
    copy = BookCopy(sach_id=book.id, ma_vach='BORROWED-T', tinh_trang='BORROWED')
    db.add(copy)
    db.commit()
    headers = auth_headers('THU_THU')
    assert client.patch(f'/api/v1/copies/{copy.id}', json={'tinh_trang': 'AVAILABLE'}, headers=headers).status_code == 409
    assert client.delete(f'/api/v1/copies/{copy.id}', headers=headers).status_code == 409
    assert client.get('/api/v1/readers', headers=auth_headers('DOC_GIA')).status_code == 403
    assert client.get('/api/v1/books', params={'page_size': 101}, headers=headers).status_code == 422


def test_expired_card_stays_expired_after_unblock(client, auth_headers, db):
    from app.models.entities import User, LibraryCard
    reader = User(ho_ten='Expired Reader', email='expired@example.test', mat_khau_hash='unused', vai_tro='DOC_GIA', trang_thai=True)
    db.add(reader)
    db.flush()
    card = LibraryCard(nguoi_dung_id=reader.id, ma_the='EXPIRED-T', ngay_cap=date(2020, 1, 1), ngay_het_han=date(2020, 2, 1), trang_thai='BLOCKED')
    db.add(card)
    db.commit()
    headers = auth_headers('THU_THU')
    response = client.patch(f'/api/v1/cards/{card.id}', json={'trang_thai': 'ACTIVE'}, headers=headers)
    assert response.status_code == 200
    assert response.json()['trang_thai'] == 'EXPIRED'
    assert client.get(f'/api/v1/readers/{reader.id}', headers=headers).json()['card']['trang_thai'] == 'EXPIRED'


def test_unknown_authors_and_untrusted_cover_scheme_rejected(client, auth_headers):
    headers = auth_headers('ADMIN')
    category = client.post('/api/v1/categories', json={'ten_the_loai': 'Input category'}, headers=headers).json()
    publisher = client.post('/api/v1/publishers', json={'ten_nxb': 'Input publisher'}, headers=headers).json()
    payload = {'ten_sach': 'Validation', 'the_loai_id': category['id'], 'nha_xuat_ban_id': publisher['id'], 'author_ids': [999999999]}
    assert client.post('/api/v1/books', json=payload, headers=headers).status_code == 404
    payload.update(author_ids=[], anh_bia='javascript:alert(1)')
    assert client.post('/api/v1/books', json=payload, headers=headers).status_code == 422
    assert client.get('/api/v1/books', params={'search': 'Validation'}, headers=headers).json()['total'] == 0

def test_reader_can_load_filter_options_but_cannot_mutate(client, auth_headers):
    headers = auth_headers('DOC_GIA')
    for endpoint, payload in [('categories', {'ten_the_loai': 'No'}), ('authors', {'ho_ten': 'No'}), ('publishers', {'ten_nxb': 'No'})]:
        assert client.get(f'/api/v1/{endpoint}', headers=headers).status_code == 200
        assert client.post(f'/api/v1/{endpoint}', json=payload, headers=headers).status_code == 403
        assert client.patch(f'/api/v1/{endpoint}/1', json=payload, headers=headers).status_code == 403
        assert client.delete(f'/api/v1/{endpoint}/1', headers=headers).status_code == 403

def test_null_patch_cannot_remove_required_values(client, auth_headers):
    headers = auth_headers('ADMIN')
    category = client.post('/api/v1/categories', json={'ten_the_loai': 'Null category'}, headers=headers).json()
    publisher = client.post('/api/v1/publishers', json={'ten_nxb': 'Null publisher'}, headers=headers).json()
    book = client.post('/api/v1/books', json={'ten_sach': 'Required values', 'the_loai_id': category['id'], 'nha_xuat_ban_id': publisher['id']}, headers=headers).json()
    for field in ['ten_sach', 'the_loai_id', 'nha_xuat_ban_id', 'author_ids']:
        assert client.patch(f"/api/v1/books/{book['id']}", json={field: None}, headers=headers).status_code == 422
    assert client.patch(f"/api/v1/categories/{category['id']}", json={'ten_the_loai': None}, headers=headers).status_code == 422
    assert client.patch(f"/api/v1/publishers/{publisher['id']}", json={'ten_nxb': None}, headers=headers).status_code == 422
    detail = client.get(f"/api/v1/books/{book['id']}", headers=headers).json()
    assert detail['ten_sach'] == 'Required values'
    assert detail['the_loai_id'] == category['id']
