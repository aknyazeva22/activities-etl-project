from dagster import define_asset_job


# Terraform
provision_infra = define_asset_job(
    name="provision_infra",
    selection="azure_psql_server",
)

# Get Input Data
get_raw_data = define_asset_job(
    name="get_raw_data",
    selection="raw_data",
)

# Load Data
load_data_job = define_asset_job(
    name="load_data_job",
    selection="raw_degustation_data",
)

# Configure dbt
dbt_profiles_job = define_asset_job(
    name="dbt_profiles_job",
    selection="dbt_profiles",
)

# Build dbt
dbt_build_job = define_asset_job(
    name="dbt_build_job",
    selection="my_dbt_assets",
)
