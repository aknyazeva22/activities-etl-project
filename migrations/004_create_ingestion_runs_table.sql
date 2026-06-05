create table if not exists audit.ingestion_runs (
    ingestion_id uuid primary key,
    source_name text not null,
    source_file_name text,
    started_at timestamptz not null,
    finished_at timestamptz,
    status text not null,
    raw_row_count integer,
    inserted_row_count integer,
    duplicate_row_count integer,
    error_message text
);
