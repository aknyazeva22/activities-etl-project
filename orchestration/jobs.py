import runpy
from dagster import op, job

# Infrastructure
@op
def create_azure_psql_server():
    runpy.run_module("scripts.create_postgresql_server", run_name="__main__")

@job
def provision_infra():
    create_azure_psql_server()
