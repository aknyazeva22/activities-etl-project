import os
import sys
from typing import Optional
import pandas as pd
import subprocess, time, socket
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.schema import CreateSchema
from dotenv import load_dotenv
from pandas import DataFrame
from pathlib import Path
from sqlalchemy.engine import Engine
from scripts.utils import determine_terraform_dir, load_terraform_outputs


CSV_PATH = 'data/degustations.csv'
TABLE_NAME = 'raw_degustation_data'

load_dotenv()
# Load environment variables
DB_PROVIDER = os.environ.get('DB_PROVIDER')
AZURE_SUBSCRIPTION_ID = os.environ.get('AZURE_SUBSCRIPTION_ID') if DB_PROVIDER == "azure" else None
AZURE_RESOURCE_GROUP_NAME = os.environ.get('AZURE_RESOURCE_GROUP_NAME') if DB_PROVIDER == "azure" else None
VM_NAME = os.environ.get('VM_NAME') if DB_PROVIDER == "azure" else None
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = "127.0.0.1" # "localhost" # we use localhost for azure also, since we use tunnel
DB_PORT = 15435 # os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME')
SCHEMA = os.environ.get('DB_SCHEMA', 'public')

def get_engine() -> Engine:
    """
    Build a SQLAlchemy Engine from environment variables.
    """
    connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    return create_engine(connection_string)

def ensure_pg_schema(engine: Engine, schema: str) -> None:
    """Postgres-only: create schema if missing."""
    with engine.begin() as conn:
        # conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        ddl = CreateSchema(schema, if_not_exists=True)
        conn.execute(ddl)
        if schema not in inspect(conn).get_schema_names():
            raise RuntimeError(f"Failed to verify schema '{schema}'")
        # try:
        #     ddl = CreateSchema(schema, if_not_exists=True)
        #     conn.execute(ddl)
    return



def read_raw_data(csv_path: str) -> DataFrame:
    """
    Read a semicolon-delimited CSV into a pandas DataFrame.
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(CSV_PATH, sep=';')

def push_to_table(
    df: DataFrame,
    engine: Engine,
    table_name: str,
    schema: Optional[str] = None,
    *,  # separates keyword parameters
    if_exists: str = "append",
    index: bool = False,
) -> None:
    """
    Append a pandas DataFrame to a SQL table.
    """
    # Ensure schema exists
    if schema is None:
        schema = inspect(engine).default_schema
    else:
        if not inspect(engine).has_schema(schema):
            ensure_pg_schema(engine, schema)

    if df.empty:
        raise ValueError("Nothing to write: DataFrame is empty.")

    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=index,
        method="multi",          # batch rows
    )
    print("CSV with raw data loaded into PostgreSQL successfully.")

if __name__ == '__main__':
    df = read_raw_data(CSV_PATH)
    engine = get_engine()
    push_to_table(
        df=df,
        engine=engine,
        table_name=TABLE_NAME,
        schema=SCHEMA,
        if_exists="append"
        )
