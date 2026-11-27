from pathlib import Path

from sqlalchemy import text

from scripts.db import get_engine

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"


def run_migrations() -> None:
    engine = get_engine()

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        raise RuntimeError(f"No migration files found in {MIGRATIONS_DIR}")

    with engine.begin() as conn:
        for migration_file in migration_files:
            sql = migration_file.read_text(encoding="utf-8")
            print(f"Running migration: {migration_file.name}")
            conn.execute(text(sql))

    print("Migrations completed.")


if __name__ == "__main__":
    run_migrations()
