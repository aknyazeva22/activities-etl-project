from dagster import Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource
from orchestration import assets, jobs

all_assets = load_assets_from_modules([assets])

resources = {
    "dbt": DbtCliResource(
        project_dir="dbt/dbt_activities",
        profiles_dir="dbt/dbt_activities",
    )
}

defs = Definitions(
    assets=assets.__all_assets__,
    resources=resources,
    jobs=[
        jobs.provision_infra,
        jobs.get_raw_data,
        jobs.load_data_job,
        jobs.dbt_profiles_job,
    ],
)
