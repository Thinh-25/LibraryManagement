"""Read-only verification through the application's actual SQLAlchemy engine."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.db.session import get_engine

EXPECTED_TABLES = {
    "nguoi_dung", "the_thu_vien", "the_loai", "tac_gia", "nha_xuat_ban", "sach",
    "sach_tac_gia", "cuon_sach", "phieu_muon", "chi_tiet_muon", "dat_truoc_sach", "tien_phat",
}


def main() -> None:
    with get_engine().connect() as connection:
        identity = connection.execute(text(
            "SELECT current_database(), current_user, inet_server_port()"
        )).one()
        tables = set(connection.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )).scalars())
        missing = EXPECTED_TABLES - tables
        if missing:
            raise RuntimeError("Missing tables: " + ", ".join(sorted(missing)))
        counts = {
            # Names are internal constants, never external input.
            table: connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one()
            for table in sorted(EXPECTED_TABLES)
        }
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        role = connection.execute(text(
            "SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname = current_user"
        )).one()
        if any(role):
            raise RuntimeError("Application role unexpectedly has administrative privileges.")
        print(json.dumps({
            "database": identity[0], "user": identity[1], "port": identity[2],
            "revision": revision, "table_count": len(EXPECTED_TABLES), "rows": counts,
            "application_role_is_admin": False,
        }, indent=2))


if __name__ == "__main__":
    main()
