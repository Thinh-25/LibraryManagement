from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import inspect, or_
from app.core.errors import BusinessError
from app.models.entities import Author, Book, BookAuthor, BookCopy, Category, LibraryCard, LoanItem, Publisher, Reservation, User
from app.repositories.catalog import CatalogRepository


def record(item):
    return {column.key: getattr(item, column.key) for column in inspect(item).mapper.column_attrs}

class CatalogService:
    def __init__(self, db):
        self.db = db
        self.repo = CatalogRepository(db)

    def get(self, model, item_id, lock=False):
        item = self.repo.get(model, item_id, lock)
        if item is None:
            raise BusinessError(404, 'Không tìm thấy dữ liệu.')
        return item

    def save(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_simple(self, model, name, page, page_size, search):
        conditions = [getattr(model, name).ilike(f'%{search}%')] if search else []
        items, total = self.repo.page(model, page, page_size, conditions)
        return dict(items=[record(item) for item in items], total=total, page=page, page_size=page_size)

    def write_simple(self, model, data, item_id=None):
        values = data.model_dump(exclude_unset=item_id is not None, mode='json')
        required = {Category: ['ten_the_loai'], Author: ['ho_ten'], Publisher: ['ten_nxb']}[model]
        self.nonnull(values, required)
        item = self.get(model, item_id, True) if item_id else model()
        for key, value in values.items():
            setattr(item, key, value)
        return record(self.save(item))

    @staticmethod
    def nonnull(values, fields):
        if any(key in values and values[key] is None for key in fields):
            raise BusinessError(422, 'Trường bắt buộc không được để trống.')

    def delete_simple(self, model, item_id):
        item = self.get(model, item_id, True)
        references = {Category: (Book, Book.the_loai_id), Publisher: (Book, Book.nha_xuat_ban_id), Author: (BookAuthor, BookAuthor.tac_gia_id)}
        target, column = references[model]
        if self.repo.exists(target, column == item_id):
            raise BusinessError(409, 'Dữ liệu đang được sách tham chiếu.')
        self.db.delete(item)
        self.db.commit()

    def book_data(self, item, detail=False):
        result = record(item)
        copies = self.repo.copies(item.id)
        result.update(authors=[{'id': author.id, 'ho_ten': author.ho_ten} for author in self.repo.authors(item.id)], available_copies=sum(copy.tinh_trang == 'AVAILABLE' for copy in copies), total_copies=len(copies), category_name=self.get(Category, item.the_loai_id).ten_the_loai, publisher_name=self.get(Publisher, item.nha_xuat_ban_id).ten_nxb)
        if detail:
            result['copies'] = [record(copy) for copy in copies]
        return result

    def list_books(self, page, page_size, **filters):
        items, total = self.repo.books(page, page_size, **filters)
        return dict(items=[self.book_data(item) for item in items], total=total, page=page, page_size=page_size)

    def write_book(self, data, item_id=None):
        values = data.model_dump(exclude_unset=item_id is not None, mode='json')
        self.nonnull(values, ['ten_sach', 'the_loai_id', 'nha_xuat_ban_id', 'author_ids'])
        author_ids = values.pop('author_ids', None)
        for key, model in [('the_loai_id', Category), ('nha_xuat_ban_id', Publisher)]:
            if key in values:
                self.get(model, values[key])
        if author_ids is not None:
            for author_id in author_ids:
                self.get(Author, author_id)
        item = self.get(Book, item_id, True) if item_id else Book()
        for key, value in values.items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.flush()
        if author_ids is not None:
            self.repo.set_authors(item.id, author_ids)
        self.db.commit()
        return self.book_data(item, True)

    def delete_book(self, item_id):
        item = self.get(Book, item_id, True)
        if self.repo.exists(BookCopy, BookCopy.sach_id == item_id) or self.repo.exists(Reservation, Reservation.sach_id == item_id):
            raise BusinessError(409, 'Sách còn bản sao hoặc lịch sử đặt trước.')
        self.db.delete(item)
        self.db.commit()

    def write_copy(self, data, book_id=None, item_id=None):
        values = data.model_dump(exclude_unset=item_id is not None)
        self.nonnull(values, ['ma_vach', 'tinh_trang'])
        if item_id:
            item = self.get(BookCopy, item_id, True)
            if item.tinh_trang == 'BORROWED' or self.repo.exists(LoanItem, LoanItem.cuon_sach_id == item_id, LoanItem.trang_thai == 'BORROWED'):
                raise BusinessError(409, 'Không được sửa cuốn sách đang mượn.')
        else:
            self.get(Book, book_id)
            item = BookCopy(sach_id=book_id)
        for key, value in values.items():
            setattr(item, key, value)
        return record(self.save(item))

    def delete_copy(self, item_id):
        item = self.get(BookCopy, item_id, True)
        if item.tinh_trang == 'BORROWED' or self.repo.exists(LoanItem, LoanItem.cuon_sach_id == item_id):
            raise BusinessError(409, 'Cuốn sách đang mượn hoặc có lịch sử mượn.')
        self.db.delete(item)
        self.db.commit()

    def reader(self, item_id, lock=False):
        item = self.get(User, item_id, lock)
        if item.vai_tro != 'DOC_GIA':
            raise BusinessError(404, 'Không tìm thấy độc giả.')
        return item

    def card_data(self, card):
        if card is None:
            return None
        result = record(card)
        if card.trang_thai == 'ACTIVE' and card.ngay_het_han < datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date():
            result['trang_thai'] = 'EXPIRED'
        return result

    def reader_data(self, reader):
        return dict(id=reader.id, ho_ten=reader.ho_ten, email=reader.email, so_dien_thoai=reader.so_dien_thoai, vai_tro=reader.vai_tro, trang_thai=reader.trang_thai, ngay_tao=reader.ngay_tao, card=self.card_data(self.repo.card(reader.id)))

    def list_readers(self, page, page_size, search):
        conditions = [User.vai_tro == 'DOC_GIA']
        if search:
            conditions.append(or_(User.ho_ten.ilike(f'%{search}%'), User.email.ilike(f'%{search}%')))
        items, total = self.repo.page(User, page, page_size, conditions)
        return dict(items=[self.reader_data(item) for item in items], total=total, page=page, page_size=page_size)

    def create_card(self, reader_id, data):
        reader = self.reader(reader_id, True)
        if not reader.trang_thai:
            raise BusinessError(409, 'Độc giả đã bị khóa.')
        if self.repo.card(reader_id):
            raise BusinessError(409, 'Độc giả đã có thẻ thư viện.')
        return self.card_data(self.save(LibraryCard(nguoi_dung_id=reader_id, trang_thai='ACTIVE', **data.model_dump())))

    def patch_card(self, item_id, data):
        card = self.get(LibraryCard, item_id, True)
        values = data.model_dump(exclude_unset=True)
        self.nonnull(values, ['ngay_het_han', 'trang_thai'])
        expiry = values.get('ngay_het_han')
        if expiry is not None and (expiry <= card.ngay_cap or expiry <= card.ngay_het_han):
            raise BusinessError(422, 'Gia hạn phải sau ngày cấp và ngày hết hạn cũ.')
        for key, value in values.items():
            setattr(card, key, value)
        return self.card_data(self.save(card))
