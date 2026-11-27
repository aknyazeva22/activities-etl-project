import os
import runpy

from dagster import AssetExecutionContext, asset
from sqlalchemy import inspect

from scripts.db import get_engine
from scripts.load_raw_data import push_to_table, read_raw_data

CSV_PATH = "data/activities.csv"
TABLE_NAME = "raw_activity_data"
SCHEMA = os.environ.get("DB_SCHEMA", "public")
SOURCE_SYSTEM = "activities_csv"


# Configure dbt
@asset(
    description="Prepared dbt profiles from infra creation step.",
    compute_kind="python",
)
def dbt_profiles(context: AssetExecutionContext) -> None:
    """
    Creates dbt profiles needed to run dbt
    """
    context.log.info("Creating profiles for dbt from the infrastructure")
    runpy.run_module("scripts.generate_profiles", run_name="__main__")


# Get csv file with activities
@asset(
    description="Raw touristic activities downloaded from the Pays de la Loire tourism API.",
    compute_kind="python",
)
def activities_file(context: AssetExecutionContext) -> None:
    """
    Download activities.csv from the Pays de la Loire tourism API.
    """
    context.log.info("Running extract step")
    runpy.run_module("scripts.download_activities_csv", run_name="__main__")


# Create raw data table
@asset(
    deps=[activities_file, dbt_profiles],
    description="Table with raw activities data.",
    compute_kind="python",
)
def activities_raw_table(context: AssetExecutionContext) -> None:
    """
    Load activities.csv into PostgreSQL as a raw table.
    """
    df = read_raw_data(CSV_PATH)
    context.log.info("Running load step")
    engine = get_engine()
    # check if tables exist
    if not inspect(engine).has_table("raw.raw_activity_data") or not inspect(engine).has_table(
        "raw_activity_data"
    ):
        runpy.run_module("scripts.run_migrations", run_name="__main__")

    push_to_table(
        df=df,
        engine=engine,
        ingestion_id=context.run_id,
        source_system=SOURCE_SYSTEM,
        csv_path=CSV_PATH,
        if_exists="append",
    )
