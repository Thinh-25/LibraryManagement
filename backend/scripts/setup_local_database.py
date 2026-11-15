"""Create an isolated local PostgreSQL instance and import the approved SQL.

Run from the repository root with backend/.venv/Scripts/python.exe.
Never changes the machine's PostgreSQL service or existing clusters.
"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

import psycopg
from psycopg import sql
from dotenv import dotenv_values
from sqlalchemy import make_url

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local"
DATA = LOCAL / "postgres"
ADMIN_FILE = LOCAL / "postgres-admin.json"
ENV_FILE = ROOT / "backend" / ".env"
PG_BIN = Path(os.environ.get("PG_BIN", r"C:\Program Files\PostgreSQL\18\bin"))
PORT = 5433


def run(*args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(
        args, check=True, cwd=ROOT, env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def run_migrations(database_url: str) -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = database_url
    run(sys.executable, "-m", "alembic", "-c", str(ROOT / "backend" / "alembic.ini"),
        "upgrade", "head", env=environment)


def main() -> None:
    if not (PG_BIN / "initdb.exe").is_file():
        raise RuntimeError("PostgreSQL tools not found; set PG_BIN to the bin directory.")
    # Preserve the existing application configuration if it targets this database.
    if ENV_FILE.exists():
        url = make_url(str(dotenv_values(ENV_FILE).get("DATABASE_URL", "")))
        if url.host not in {"localhost", "127.0.0.1"} or (
            url.port, url.database, url.username
        ) != (PORT, "library_management", "library_app") or not url.password:
            raise RuntimeError("Existing backend/.env targets another database; refusing to overwrite.")
        app_password = url.password
    else:
        app_password = secrets.token_hex(32)

    LOCAL.mkdir(exist_ok=True)
    if not ADMIN_FILE.exists():
        if DATA.exists():
            raise RuntimeError("Existing cluster has no project credentials; refusing to modify it.")
        ADMIN_FILE.write_text(json.dumps({"password": secrets.token_hex(32)}), encoding="utf-8")
    admin_password = json.loads(ADMIN_FILE.read_text(encoding="utf-8"))["password"]

    if not (DATA / "PG_VERSION").exists():
        password_file = LOCAL / "initdb-password"
        try:
            password_file.write_text(admin_password + "\n", encoding="utf-8")
            run(str(PG_BIN / "initdb.exe"), "-D", str(DATA), "-U", "library_owner",
                "--auth=scram-sha-256", "--encoding=UTF8", "--locale=C",
                "--pwfile=" + str(password_file))
        finally:
            password_file.unlink(missing_ok=True)

    status = subprocess.run(
        [str(PG_BIN / "pg_ctl.exe"), "-D", str(DATA), "status"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if status.returncode != 0:
        run(str(PG_BIN / "pg_ctl.exe"), "-D", str(DATA), "-l", str(LOCAL / "postgres.log"),
            "-o", "-h 127.0.0.1 -p 5433", "-w", "start")

    connection_args = dict(host="127.0.0.1", port=PORT, user="library_owner",
                           password=admin_password, dbname="postgres", connect_timeout=5)
    with psycopg.connect(**connection_args, autocommit=True) as connection:
        role = connection.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", ("library_app",)).fetchone()
        if not role:
            connection.execute(sql.SQL("CREATE ROLE library_app LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE").format(sql.Literal(app_password)))
        database = connection.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("library_management",)).fetchone()
        if not database:
            connection.execute("CREATE DATABASE library_management OWNER library_app ENCODING 'UTF8' TEMPLATE template0")

    if not ENV_FILE.exists():
        ENV_FILE.write_text(
            "DATABASE_URL=postgresql+psycopg://library_app:" + app_password
            + "@127.0.0.1:5433/library_management\n"
            + 'CORS_ORIGINS=["http://localhost:5000"]\n', encoding="utf-8",
        )

    # Reject unversioned/nonempty databases instead of importing over existing tables.
    with psycopg.connect(host="127.0.0.1", port=PORT, user="library_app",
                         password=app_password, dbname="library_management", connect_timeout=5) as connection:
        tables = {row[0] for row in connection.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )}
        if tables and "alembic_version" not in tables:
            raise RuntimeError("Database is not empty and has no Alembic history; refusing to import.")

    local_url = "postgresql+psycopg://library_app:" + app_password + "@127.0.0.1:5433/library_management"
    run_migrations(local_url)
    print("Database ready: 127.0.0.1:5433/library_management (credentials saved in backend/.env).")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"Setup refused: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        # Do not print connection strings/passwords or SQL parameters.
        print(f"Setup failed ({type(exc).__name__}). Check local PostgreSQL logs and configuration.", file=sys.stderr)
        sys.exit(1)
