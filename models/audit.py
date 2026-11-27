from dataclasses import dataclass
from datetime import datetime

from pandas import DataFrame

from exceptions import AuditWriteError


@dataclass
class AuditRecord:
    """
    Audit record for an ingestion, written to the table 'audit.raw_ingestion_runs'.
    """

    ingestion_id: str
    source_file_name: str
    source_system: str
    status: str
    raw_row_count: int
    started_at: datetime
    finished_at: datetime | None = None
    inserted_row_count: int | None = None
    duplicate_row_count: int | None = None
    error_message: str | None = None

    def __post_init__(self):
        """Called automatically after __init__ by the dataclass."""
        if not self.is_valid():
            raise AuditWriteError("Audit record is missing required fields")

        return

    def to_dict(self) -> dict[str, str | int | datetime | None]:
        return {
            "ingestion_id": self.ingestion_id,
            "source_file_name": self.source_file_name,
            "source_system": self.source_system,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "raw_row_count": self.raw_row_count,
            "inserted_row_count": self.inserted_row_count,
            "duplicate_row_count": self.duplicate_row_count,
            "error_message": self.error_message,
        }

    def to_df(self) -> DataFrame:
        return DataFrame.from_dict(self.to_dict(), orient="index").T

    def is_valid(self) -> bool:
        return (
            self.ingestion_id is not None
            and self.source_file_name is not None
            and self.source_system is not None
        )
