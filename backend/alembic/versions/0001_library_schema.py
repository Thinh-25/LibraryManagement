"""Import the supplied PostgreSQL schema and sample data.

Revision ID: 0001_library_schema
Revises:
"""
from pathlib import Path

from alembic import op
from sqlalchemy import DDL

revision = "0001_library_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    source = Path(__file__).resolve().parents[2] / "sql" / "library_management.sql"
    # Alembic owns the transaction; omit only the file's outer BEGIN/COMMIT.
    statements = "\n".join(
        line for line in source.read_text(encoding="utf-8-sig").splitlines()
        if line.strip().upper() not in {"BEGIN;", "COMMIT;"}
    )
    if op.get_context().as_sql:
        op.execute(DDL(statements))
    else:
        op.get_bind().exec_driver_sql(statements)


def downgrade() -> None:
    raise RuntimeError("Destructive rollback is disabled: back up and review the schema manually.")
