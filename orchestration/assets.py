import os
import runpy
from dagster import AssetExecutionContext, asset
from dagster_dbt import dbt_assets

# Infrastructure
@asset(compute_kind="python")
def azure_psql_server(context: AssetExecutionContext) -> None:
    context.log.info("Create infrastructure with terraform")
    runpy.run_module("scripts.create_postgresql_server", run_name="__main__")


# Extract
@asset(compute_kind="python")
def raw_data(context: AssetExecutionContext) -> None:
    context.log.info("Running extract step")
    runpy.run_module("scripts.download_raw_data", run_name="__main__")

# Load
@asset(
    deps=[azure_psql_server],
    description="Create dbt profiles from infra creation step.",
    compute_kind="python",
)
def dbt_profiles(context: AssetExecutionContext) -> None:
    context.log.info("Creating profiles for dbt from the infrastructure")
    runpy.run_module("scripts.generate_profiles", run_name="__main__")

# Load
@asset(
    deps=[raw_data, azure_psql_server, dbt_profiles],
    description="Load degustations.csv into PostgreSQL as a raw table.",
    compute_kind="python",
)
def raw_degustation_data(context: AssetExecutionContext) -> None:
    context.log.info("Running load step")
    runpy.run_module("scripts.load_raw_data", run_name="__main__")
