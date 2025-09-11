from pathlib import Path
from dagster import AssetExecutionContext, Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from orchestration import assets, jobs

all_assets = load_assets_from_modules([assets])

# Points to the dbt project path
dbt_project_directory = Path(__file__).absolute().parent.parent / "dbt" / "dbt_activities"
dbt_project = DbtProject(project_dir=dbt_project_directory)



# Compiles the dbt project & allow Dagster to build an asset graph
dbt_project.prepare_if_dev()

dbt_cli = DbtCliResource(
    project_dir=str(dbt_project_directory),
    profiles_dir=str(dbt_project_directory),
    target="dev",
)

# Yields Dagster events streamed from the dbt CLI
@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context: AssetExecutionContext, dbt: DbtCliResource):
    args = [
        "build",
        "--project-dir", str(dbt_project_directory),
        "--profiles-dir", str(dbt_project_directory),
        "--target", "dev",
    ]
    yield from dbt.cli(["build"], context=context).stream()

resources = {
    "dbt": dbt_cli
}

defs = Definitions(
    assets=[
        dbt_models,
        assets.dbt_profiles,
        assets.raw_data,
        assets.raw_degustation_data,
    ],
    resources=resources,
    jobs=[
        jobs.provision_infra,
    ],
)
