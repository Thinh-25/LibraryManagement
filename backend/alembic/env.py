from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app import models  # noqa: F401 -- registers future model imports
from app.core.config import get_settings
from app.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = get_settings().database_url
if database_url is None:
    raise RuntimeError("Configure DATABASE_URL in backend/.env before running Alembic.")

target_metadata = Base.metadata

# Imported SQL is the baseline until ORM mappings exist. Empty metadata would
# otherwise make autogenerate propose dropping every imported business table.
if getattr(config.cmd_opts, "autogenerate", False) and not target_metadata.tables:
    raise RuntimeError("ORM metadata is empty; map the imported schema before using autogenerate.")


def run_migrations_offline() -> None:
    context.configure(
        url=database_url.get_secret_value(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(database_url.get_secret_value(), poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
