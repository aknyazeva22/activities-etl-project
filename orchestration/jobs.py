from dagster import define_asset_job

# Terraform
provision_infra = define_asset_job(
    name="provision_infra",
    selection="azure_psql_server",
)

# Get Input Data
raw_data_job = define_asset_job(
    name="raw_data_job",
    selection="raw_data",
)

# Load Data
load_data_job = define_asset_job(
    name="load_data_job",
    selection="loaded_data",
)
