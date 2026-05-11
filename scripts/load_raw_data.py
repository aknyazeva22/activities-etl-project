from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pandas as pd
from pandas import DataFrame
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema


def ensure_pg_schema(engine: Engine, schema: str) -> None:
    """Postgres-only: create schema if missing."""
    ddl = CreateSchema(schema, if_not_exists=True)

    with engine.begin() as conn:
        try:
            conn.execute(ddl)
        except Exception as e:
            raise RuntimeError(f"Failed to create schema '{schema}': {e}") from e

    return


def read_raw_data(csv_path: str) -> DataFrame:
    """
    Read a semicolon-delimited CSV into a pandas DataFrame.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(csv_path, sep=";")


def add_technical_metadata(
    df: DataFrame,
    *,
    ingestion_id: str,
    ingested_at: datetime | None = None,
    source_file_name: str,
    source_system: str,
    source_row_number: int | None = None,
    source_hash: str | None = None,
) -> DataFrame:
    """
    Add technical metadata columns to the DataFrame.
    """
    out = df.copy()
    if ingested_at is None:
        ingested_at = datetime.now(UTC)

    if source_row_number is None:
        source_row_number = out.index.astype("int64") + 1

    if source_hash is None:
        # add hash column for deduping
        row_as_text = out.astype("string").fillna("").agg("|".join, axis=1)
        source_hash = row_as_text.apply(lambda s: sha256(s.encode("utf-8")).hexdigest())

    out["source_row_number"] = source_row_number
    out["ingestion_id"] = ingestion_id
    out["ingested_at"] = ingested_at
    out["source_file_name"] = source_file_name
    out["source_system"] = source_system
    out["source_hash"] = source_hash

    return out


def insert_on_conflict_do_nothing(table_name, conn, keys, data_iter):
    rows = [dict(zip(keys, row, strict=True)) for row in data_iter]

    if not rows:
        return 0

    stmt = insert(table_name.table).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["source_hash"])

    result = conn.execute(stmt)
    return result.rowcount


def push_to_table(
    df: DataFrame,
    engine: Engine,
    *,
    csv_path: str,
    ingestion_id: str,
    source_system: str,
    if_exists: str = "append",
    index: bool = False,
) -> None:
    """
    Push a pandas DataFrame to a SQL table.
    """
    # Ensure schema exists

    if not inspect(engine).has_schema("raw"):
        ensure_pg_schema(engine, "raw")

    if df.empty:
        raise ValueError("Nothing to write: DataFrame is empty.")

    df = add_technical_metadata(
        df,
        ingestion_id=ingestion_id,
        ingested_at=datetime.now(UTC),
        source_file_name=Path(csv_path).name,
        source_system=source_system,
    )

    df.to_sql(
        name="raw_degustation_data",
        con=engine,
        schema="raw",
        if_exists=if_exists,
        index=index,
        method=insert_on_conflict_do_nothing,
    )
    print("CSV with raw data loaded into PostgreSQL successfully.")
