import os
import runpy
from dagster import AssetExecutionContext, asset
from dagster_dbt import dbt_assets

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

# Get csv file with degustations
@asset(
    description="Raw degustation activities downloaded from the Pays de la Loire tourism API.", 
    compute_kind="python"
)
def degustations_file(context: AssetExecutionContext) -> None:
    """
    Download degustations.csv from the Pays de la Loire tourism API.
    """
    context.log.info("Running extract step")
    runpy.run_module("scripts.download_degustation_csv", run_name="__main__")

# Create raw data table
@asset(
    deps=[degustations_file, dbt_profiles],
    description="Raw degustation table.",
    compute_kind="python",
)
def degustations_raw_table(context: AssetExecutionContext) -> None:
    """
    Load degustations.csv into PostgreSQL as a raw table.
    """
    context.log.info("Running load step")
    runpy.run_module("scripts.load_raw_data", run_name="__main__")
