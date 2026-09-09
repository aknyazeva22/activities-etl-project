class AuditWriteError(RuntimeError):
    """Raised when an audit record cannot be persisted."""

    pass


class EmptySourceFileError(ValueError):
    """Raised when a source CSV file contains no data rows."""

    pass


class SchemaCreationError(RuntimeError):
    """Raised when a required database schema cannot be created."""

    pass
