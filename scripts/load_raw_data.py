import logging
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pandas as pd
from pandas import DataFrame
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema

from exceptions import AuditWriteError, EmptySourceFileError, SchemaCreationError
from models.audit import AuditRecord

logger = logging.getLogger(__name__)


def ensure_pg_schema(engine: Engine, schema: str) -> None:
    """Postgres-only: create schema if missing."""
    if not inspect(engine).has_schema(schema):
        ddl = CreateSchema(schema, if_not_exists=True)

        with engine.begin() as conn:
            try:
                conn.execute(ddl)
            except Exception as e:
                raise SchemaCreationError(f"Failed to create schema '{schema}': {e}") from e

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


def write_audit(
    engine: Engine,
    audit_record: AuditRecord,
) -> None:
    """Write an audit record for an ingestion."""
    if not audit_record.is_valid():
        raise AuditWriteError("Audit record is missing required fields")

    if audit_record.finished_at is None:
        audit_record.finished_at = datetime.now(UTC)

    audit_row = audit_record.to_df()
    audit_row.to_sql(
        name="ingestion_runs",
        con=engine,
        schema="audit",
        if_exists="append",
        index=False,
    )

    return


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
    ensure_pg_schema(engine, "raw")

    ingestion_time = datetime.now(UTC)

    if df.empty:
        audit_record = AuditRecord(
            ingestion_id=ingestion_id,
            source_file_name=Path(csv_path).name,
            source_system=source_system,
            started_at=ingestion_time,
            status="failed",
            raw_row_count=0,
            error_message="Source file contains 0 rows",
        )

        write_audit(
            engine=engine,
            audit_record=audit_record,
        )

        raise EmptySourceFileError("Source file contains 0 rows")

    df = add_technical_metadata(
        df,
        ingestion_id=ingestion_id,
        ingested_at=ingestion_time,
        source_file_name=Path(csv_path).name,
        source_system=source_system,
    )

    try:
        attempted_rows = len(df)

        inserted_rows = (
            df.to_sql(
                name="raw_degustation_data",
                con=engine,
                schema="raw",
                if_exists=if_exists,
                index=index,
                method=insert_on_conflict_do_nothing,
            )
            or 0
        )  # convert None to 0
        logger.info(
            "CSV with raw data loaded into PostgreSQL successfully: %d rows",
            inserted_rows,
        )

        duplicate_rows = attempted_rows - inserted_rows

        audit_record = AuditRecord(
            ingestion_id=ingestion_id,
            source_file_name=Path(csv_path).name,
            source_system=source_system,
            started_at=ingestion_time,
            status="success",
            raw_row_count=attempted_rows,
            inserted_row_count=inserted_rows,
            duplicate_row_count=duplicate_rows,
        )
        write_audit(
            engine=engine,
            audit_record=audit_record,
        )
        logger.info("Audit table updated.")

    except Exception as e:
        audit_record = AuditRecord(
            ingestion_id=ingestion_id,
            source_file_name=Path(csv_path).name,
            source_system=source_system,
            started_at=ingestion_time,
            status="failed",
            raw_row_count=len(df),
            error_message=str(e),
        )
        write_audit(
            engine=engine,
            audit_record=audit_record,
        )
        logger.error("Load failed: %s", e)
        raise
