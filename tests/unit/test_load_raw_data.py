# pytest unit tests for load_raw_data.py

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from scripts.load_raw_data import (
    AuditRecord,
    AuditWriteError,
    EmptySourceFileError,
    push_to_table,
    read_raw_data,
)


def test_read_raw_data():
    csv_path = "data/degustations.csv"
    df = read_raw_data(csv_path)
    assert not df.empty


def test_read_raw_data_file_not_found():
    csv_path = "data/empty.csv"
    with pytest.raises(FileNotFoundError) as excinfo:
        read_raw_data(csv_path)
        assert "Source file contains 0 rows" in str(excinfo.value)


def test_push_to_table_empty():
    df = pd.DataFrame()

    with (
        pytest.raises(EmptySourceFileError),
        patch("scripts.load_raw_data.ensure_pg_schema"),
    ):
        push_to_table(
            df=df,
            engine=MagicMock(),
            ingestion_id="ingestion_id",
            source_system="source_system",
            csv_path="data/degustations.csv",
            if_exists="append",
        )


def test_audit_record_is_valid():
    valid_record = AuditRecord(
        ingestion_id="ingestion_id",
        source_file_name="source_file_name",
        source_system="source_system",
        started_at=datetime.now(UTC),
        status="success",
        raw_row_count=100,
    )
    assert valid_record.is_valid()


def test_audit_record_is_invalid():
    with pytest.raises(AuditWriteError) as excinfo:
        AuditRecord(
            ingestion_id=None,
            source_file_name="source_file_name",
            source_system="source_system",
            started_at=datetime.now(UTC),
            status="success",
            raw_row_count=100,
        )
        assert "Audit record is missing required fields" in str(excinfo.value)
