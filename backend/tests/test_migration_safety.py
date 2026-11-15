from pathlib import Path
from types import SimpleNamespace
import pytest

import os
import subprocess
import sys


def test_autogenerate_refuses_empty_orm_metadata_before_connecting(monkeypatch):
    from sqlalchemy import MetaData
    from app.db.base import Base
    from alembic.config import Config
    from alembic import command
    monkeypatch.setattr(Base, "metadata", MetaData())
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"),
                    cmd_opts=SimpleNamespace(autogenerate=True))
    with pytest.raises(RuntimeError, match="ORM metadata is empty"):
        command.revision(config, message="must not generate destructive changes", autogenerate=True)


def test_orm_metadata_matches_migrated_postgresql_schema(test_engine):
    from alembic.migration import MigrationContext
    from alembic.autogenerate import compare_metadata
    from app.db.base import Base
    from app import models
    with test_engine.connect() as connection:
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []


def test_local_setup_overrides_inherited_database_url(monkeypatch):
    from scripts import setup_local_database

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://unused:unused@remote.invalid/other")
    captured = {}

    def capture_run(*args, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(setup_local_database, "run", capture_run)
    local_url = "postgresql+psycopg://local:example@127.0.0.1:5433/library_management"
    setup_local_database.run_migrations(local_url)
    assert captured["env"]["DATABASE_URL"] == local_url
