import os
import runpy
from dagster import AssetExecutionContext, asset
from dagster_dbt import dbt_assets

# Infrastructure
@asset
def azure_psql_server(context: AssetExecutionContext) -> None:
    context.log.info("Create infrastructure with terraform")
    runpy.run_module("scripts.create_postgresql_server", run_name="__main__")


# Extract
@asset
def raw_data(context: AssetExecutionContext) -> None:
    context.log.info("Running extract step")
    # TODO: add raw data extraction here

# Load
@asset(
    deps=[raw_data, azure_psql_server],
    description="Load degustations.csv into PostgreSQL as a raw table."
)
def loaded_data(context: AssetExecutionContext) -> None:
    context.log.info("Running load step")
    runpy.run_module("scripts.load_raw_data", run_name="__main__")


__all_assets__ = [
    azure_psql_server,
    raw_data,
    loaded_data,
]
