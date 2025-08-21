import os
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
from pandas import DataFrame
from pathlib import Path
from sqlalchemy.engine import Engine
from utils import determine_terraform_dir, load_terraform_outputs


CSV_PATH = 'data/degustations.csv'
TABLE_NAME = 'raw_degustation_data'
SCHEMA = 'public'

load_dotenv()
# Load environment variables
DB_PROVIDER = os.environ.get('DB_PROVIDER')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = "localhost" if DB_PROVIDER == "local" else None
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME')

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
    elif db_provider == "local":
        connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        sys.exit(f"[fatal] provider type is not supported: {db_provider}")

    return create_engine(connection_string)

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
