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
AZURE_RESOURCE_GROUP_NAME = os.environ.get('AZURE_RESOURCE_GROUP_NAME') if DB_PROVIDER == "azure" else None
VM_NAME = os.environ.get('VM_NAME') if DB_PROVIDER == "azure" else None
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = "localhost" # we use localhost for azure also, since we use tunnel
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME')
SCHEMA = os.environ.get('DB_SCHEMA', 'public')

def get_engine() -> Engine:
    """
    Build a SQLAlchemy Engine from terraform outputs.
    """
    if DB_PROVIDER == "azure":
        # get connection string from terraform outputs
        tf_dir = determine_terraform_dir()
        outputs = load_terraform_outputs(tf_dir)
        try:
            connection_string = outputs["postgres_example_conn_str"]["value"]
        except KeyError as missing:
            sys.exit(f"[fatal] missing key in terraform outputs: {missing}")

        try:
            proc = subprocess.Popen([
                "az","network","bastion","tunnel",
                "--name","bastion-host",
                "--resource-group", AZURE_RESOURCE_GROUP_NAME,
                f"--target-resource-id","/subscriptions/<sub>/resourceGroups/{AZURE_RESOURCE_GROUP_NAME}/providers/Microsoft.Compute/virtualMachines/{VM_NAME}",
                "--resource-port", "5432","--port", str(DB_PORT)
            ])
            # Wait until local port is open
            for _ in range(60):
                with socket.socket() as s:
                    if s.connect_ex((DB_HOST, int(DB_PORT))) == 0:
                        break
                time.sleep(1)
        except Exception as tunnel_error:
            sys.exit(f"[fatal] cannot open tunnel: {tunnel_error}")

    elif DB_PROVIDER == "local":
        connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        sys.exit(f"[fatal] provider type is not supported: {DB_PROVIDER}")

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
