# pytest unit tests for load_raw_data.py

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from scripts.load_raw_data import (
    AuditRecord,
    AuditWriteError,
    EmptySourceFileError,
    add_technical_metadata,
    push_to_table,
    read_raw_data,
    write_audit,
)


def test_read_raw_data(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1;col2\n1;a\n2;b")

    df = read_raw_data(str(csv_file))
    assert len(df) == 2
    assert "col1" in df.columns


def test_read_raw_data_file_not_found():
    csv_path = "data/empty.csv"
    with pytest.raises(FileNotFoundError) as excinfo:
        read_raw_data(csv_path)

    assert "CSV file not found" in str(excinfo.value)


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


def test_add_technical_metadata():
    df = pd.DataFrame({"col1": [1, 2, 3, 3], "col2": ["a", "b", "c", "c"]})
    df = add_technical_metadata(
        df,
        ingestion_id="ingestion_id",
        source_file_name="source_file_name",
        source_system="source_system",
    )
    assert "source_row_number" in df.columns
    assert "ingestion_id" in df.columns
    assert "ingested_at" in df.columns
    assert "source_file_name" in df.columns
    assert "source_system" in df.columns

    assert df["source_row_number"].tolist() == [1, 2, 3, 4]
    assert df["ingestion_id"].tolist() == ["ingestion_id"] * 4
    assert isinstance(df["ingested_at"][0], datetime)
    assert df["source_file_name"].tolist() == ["source_file_name"] * 4
    assert df["source_system"].tolist() == ["source_system"] * 4

    # check that the source hash is the same for duplicate rows
    assert df["source_hash"][2] == df["source_hash"][3]


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


def test_write_audit_add_finished_at():
    engine = MagicMock()
    audit_record = AuditRecord(
        ingestion_id="ingestion_id",
        source_file_name="source_file_name",
        source_system="source_system",
        started_at=datetime.now(UTC),
        status="success",
        raw_row_count=100,
    )
    write_audit(engine, audit_record)
    assert audit_record.finished_at
    assert isinstance(audit_record.finished_at, datetime)
    assert audit_record.finished_at > audit_record.started_at
