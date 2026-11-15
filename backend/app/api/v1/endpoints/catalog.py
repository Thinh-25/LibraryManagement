from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import require_roles
from app.models.entities import Author, Book, Category, Publisher
from app.schemas.catalog import AuthorCreate, AuthorPatch, BookCreate, BookPatch, CardCreate, CardPatch, CategoryCreate, CategoryPatch, CopyCreate, CopyPatch, PublisherCreate, PublisherPatch
from app.services.catalog import CatalogService, record

router = APIRouter(tags=['Danh mục và độc giả'])
DB = Annotated[Session, Depends(get_db)]
Page = Annotated[int, Query(ge=1)]
Size = Annotated[int, Query(ge=1, le=100)]
staff = [Depends(require_roles('ADMIN', 'THU_THU'))]
readers = [Depends(require_roles('ADMIN', 'THU_THU', 'DOC_GIA'))]

@router.get('/books', dependencies=readers)
def books(db: DB, page: Page = 1, page_size: Size = 20, search: str | None = None, category_id: int | None = None, author_id: int | None = None, publisher_id: int | None = None):
    return CatalogService(db).list_books(page, page_size, search=search, category_id=category_id, author_id=author_id, publisher_id=publisher_id)

@router.get('/books/{item_id}', dependencies=readers)
def book(item_id: int, db: DB):
    service = CatalogService(db)
    return service.book_data(service.get(Book, item_id), True)

@router.post('/books', status_code=201, dependencies=staff)
def create_book(body: BookCreate, db: DB):
    return CatalogService(db).write_book(body)

@router.patch('/books/{item_id}', dependencies=staff)
def patch_book(item_id: int, body: BookPatch, db: DB):
    return CatalogService(db).write_book(body, item_id)

@router.delete('/books/{item_id}', status_code=204, dependencies=staff)
def delete_book(item_id: int, db: DB):
    CatalogService(db).delete_book(item_id)
    return Response(status_code=204)

@router.post('/books/{item_id}/copies', status_code=201, dependencies=staff)
def create_copy(item_id: int, body: CopyCreate, db: DB):
    return CatalogService(db).write_copy(body, book_id=item_id)

@router.patch('/copies/{item_id}', dependencies=staff)
def patch_copy(item_id: int, body: CopyPatch, db: DB):
    return CatalogService(db).write_copy(body, item_id=item_id)

@router.delete('/copies/{item_id}', status_code=204, dependencies=staff)
def delete_copy(item_id: int, db: DB):
    CatalogService(db).delete_copy(item_id)
    return Response(status_code=204)

@router.get('/readers', dependencies=staff)
def list_readers(db: DB, page: Page = 1, page_size: Size = 20, search: str | None = None):
    return CatalogService(db).list_readers(page, page_size, search)

@router.get('/readers/{item_id}', dependencies=staff)
def get_reader(item_id: int, db: DB):
    service = CatalogService(db)
    return service.reader_data(service.reader(item_id))

@router.post('/readers/{item_id}/card', status_code=201, dependencies=staff)
def create_card(item_id: int, body: CardCreate, db: DB):
    return CatalogService(db).create_card(item_id, body)

@router.patch('/cards/{item_id}', dependencies=staff)
def patch_card(item_id: int, body: CardPatch, db: DB):
    return CatalogService(db).patch_card(item_id, body)

@router.get('/categories', dependencies=readers)
def list_categories(db: DB, page: Page = 1, page_size: Size = 20, search: str | None = None):
    return CatalogService(db).list_simple(Category, 'ten_the_loai', page, page_size, search)

@router.get('/categories/{item_id}', dependencies=readers)
def get_category(item_id: int, db: DB):
    return record(CatalogService(db).get(Category, item_id))

@router.post('/categories', status_code=201, dependencies=staff)
def create_category(body: CategoryCreate, db: DB):
    return CatalogService(db).write_simple(Category, body)

@router.patch('/categories/{item_id}', dependencies=staff)
def patch_category(item_id: int, body: CategoryPatch, db: DB):
    return CatalogService(db).write_simple(Category, body, item_id)

@router.delete('/categories/{item_id}', status_code=204, dependencies=staff)
def delete_category(item_id: int, db: DB):
    CatalogService(db).delete_simple(Category, item_id)
    return Response(status_code=204)

@router.get('/authors', dependencies=readers)
def list_authors(db: DB, page: Page = 1, page_size: Size = 20, search: str | None = None):
    return CatalogService(db).list_simple(Author, 'ho_ten', page, page_size, search)

@router.get('/authors/{item_id}', dependencies=readers)
def get_author(item_id: int, db: DB):
    return record(CatalogService(db).get(Author, item_id))

@router.post('/authors', status_code=201, dependencies=staff)
def create_author(body: AuthorCreate, db: DB):
    return CatalogService(db).write_simple(Author, body)

@router.patch('/authors/{item_id}', dependencies=staff)
def patch_author(item_id: int, body: AuthorPatch, db: DB):
    return CatalogService(db).write_simple(Author, body, item_id)

@router.delete('/authors/{item_id}', status_code=204, dependencies=staff)
def delete_author(item_id: int, db: DB):
    CatalogService(db).delete_simple(Author, item_id)
    return Response(status_code=204)

@router.get('/publishers', dependencies=readers)
def list_publishers(db: DB, page: Page = 1, page_size: Size = 20, search: str | None = None):
    return CatalogService(db).list_simple(Publisher, 'ten_nxb', page, page_size, search)

@router.get('/publishers/{item_id}', dependencies=readers)
def get_publisher(item_id: int, db: DB):
    return record(CatalogService(db).get(Publisher, item_id))

@router.post('/publishers', status_code=201, dependencies=staff)
def create_publisher(body: PublisherCreate, db: DB):
    return CatalogService(db).write_simple(Publisher, body)

@router.patch('/publishers/{item_id}', dependencies=staff)
def patch_publisher(item_id: int, body: PublisherPatch, db: DB):
    return CatalogService(db).write_simple(Publisher, body, item_id)

@router.delete('/publishers/{item_id}', status_code=204, dependencies=staff)
def delete_publisher(item_id: int, db: DB):
    CatalogService(db).delete_simple(Publisher, item_id)
    return Response(status_code=204)
