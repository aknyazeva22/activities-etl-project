import os
import runpy
from dagster import AssetExecutionContext, asset
from dagster_dbt import dbt_assets

# Configure dbt
@asset(
    description="Create dbt profiles from infra creation step.",
    compute_kind="python",
)
def dbt_profiles(context: AssetExecutionContext) -> None:
    context.log.info("Creating profiles for dbt from the infrastructure")
    runpy.run_module("scripts.generate_profiles", run_name="__main__")

# Get csv file with degustations
@asset(compute_kind="python")
def degustations_file(context: AssetExecutionContext) -> None:
    context.log.info("Running extract step")
    runpy.run_module("scripts.download_degustation_csv", run_name="__main__")

# Create raw data table
@asset(
    deps=[degustations_file, dbt_profiles],
    description="Load degustations.csv into PostgreSQL as a raw table.",
    compute_kind="python",
)
def degustations_raw_table(context: AssetExecutionContext) -> None:
    context.log.info("Running load step")
    runpy.run_module("scripts.load_raw_data", run_name="__main__")
