from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session
from app.models.entities import Author, Book, BookAuthor, BookCopy, Category, LibraryCard, Publisher, User

class CatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, model, item_id, lock=False):
        query = select(model).where(model.id == item_id)
        if lock:
            query = query.with_for_update()
        return self.db.scalar(query)

    def exists(self, model, *conditions):
        return self.db.scalar(select(model).where(*conditions).limit(1)) is not None

    def page(self, model, page, page_size, conditions=()):
        query = select(model).where(*conditions)
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        items = self.db.scalars(query.order_by(model.id).offset((page-1)*page_size).limit(page_size)).all()
        return items, total

    def books(self, page, page_size, search=None, category_id=None, author_id=None, publisher_id=None):
        conditions = []
        if search:
            conditions.append(or_(Book.ten_sach.ilike(f'%{search}%'), Book.isbn.ilike(f'%{search}%')))
        if category_id:
            conditions.append(Book.the_loai_id == category_id)
        if publisher_id:
            conditions.append(Book.nha_xuat_ban_id == publisher_id)
        if author_id:
            conditions.append(Book.id.in_(select(BookAuthor.sach_id).where(BookAuthor.tac_gia_id == author_id)))
        return self.page(Book, page, page_size, conditions)

    def authors(self, book_id):
        return self.db.scalars(select(Author).join(BookAuthor, BookAuthor.tac_gia_id == Author.id).where(BookAuthor.sach_id == book_id).order_by(Author.id)).all()

    def copies(self, book_id):
        return self.db.scalars(select(BookCopy).where(BookCopy.sach_id == book_id).order_by(BookCopy.id)).all()

    def set_authors(self, book_id, author_ids):
        self.db.execute(delete(BookAuthor).where(BookAuthor.sach_id == book_id))
        self.db.add_all([BookAuthor(sach_id=book_id, tac_gia_id=item) for item in author_ids])

    def card(self, reader_id):
        return self.db.scalar(select(LibraryCard).where(LibraryCard.nguoi_dung_id == reader_id))
