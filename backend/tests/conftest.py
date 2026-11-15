"""Integration fixtures: a dedicated PostgreSQL database, never the app DB."""
import os
from uuid import uuid4
from pathlib import Path
from dotenv import dotenv_values

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, make_url
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    from app.core.config import get_settings
    monkeypatch.setenv("JWT_SECRET", "isolated-test-signing-key-never-use-in-production-123456789")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def test_engine():
    value = os.environ.get("TEST_DATABASE_URL") or dotenv_values(
        Path(__file__).resolve().parents[2] / ".local" / "test-database.env"
    ).get("TEST_DATABASE_URL")
    if not value:
        pytest.fail("Set TEST_DATABASE_URL to the isolated library_management_test database.")
    url = make_url(value)
    if url.database != "library_management_test":
        pytest.fail("Refusing tests outside the isolated library_management_test database.")
    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture
def db(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def client(db):
    from app.main import app
    from app.dependencies.database import get_db

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_headers(db):
    def headers(role="ADMIN", user_id=None):
        from app.models.entities import User
        from app.core.security import hash_password, create_access_token

        user = db.get(User, user_id) if user_id else None
        if user is None:
            user = User(
                ho_ten="Test " + role, email=uuid4().hex + "@example.test",
                mat_khau_hash=hash_password("ValidPassword123!"), vai_tro=role,
                trang_thai=True, auth_version=0, must_change_password=False,
            )
            db.add(user)
            db.flush()
            db.commit()
        return {"Authorization": "Bearer " + create_access_token(user)}
    return headers
