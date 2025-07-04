import os
import runpy
from dagster import AssetExecutionContext, asset
from dagster_dbt import dbt_assets


# Extract
@asset
def raw_data(context: AssetExecutionContext) -> None:
    context.log.info("Running extract step")
    # TODO: add raw data extraction here

# Load
@asset(
    deps=[raw_data],
    description="Load degustations.csv into PostgreSQL as a raw table."
)
def loaded_data(context: AssetExecutionContext) -> None:
    context.log.info("Running load step")
    runpy.run_module("scripts.load_raw_data", run_name="__main__")


__all_assets__ = [
    raw_data,
    loaded_data,
]
