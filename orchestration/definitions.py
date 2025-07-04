from dagster import Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource
from orchestration import assets

all_assets = load_assets_from_modules([assets])

resources = {
    "dbt": DbtCliResource(
        project_dir="dbt/dbt_activities",
        profiles_dir="dbt/dbt_activities",
    )
}

defs = Definitions(
    assets=[assets.raw_data, assets.loaded_data],
    resources=resources,
)
