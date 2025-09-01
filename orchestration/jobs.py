import os
import runpy
from dagster import op, job, OpExecutionContext
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from orchestration.resources.bastion_tunnel import BastionTunnelResource


load_dotenv()

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

# Infrastructure
@op
def create_azure_psql_server():
    runpy.run_module("scripts.create_postgresql_server", run_name="__main__")

@job
def provision_infra():
    create_azure_psql_server()

@op(required_resource_keys={"bastion"})
def query_pg(context: OpExecutionContext):
    r: BastionTunnelResource = context.resources.bastion  # type: ignore[attr-defined]
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{r.host}:{r.port}/{DB_NAME}"
    engine = create_engine(url, pool_pre_ping=True, future=True)
    with engine.begin() as conn:
        context.log.info(conn.execute(text("select version()")).scalar())

@job(resource_defs={"bastion": BastionTunnelResource()})
def tunnel_then_query():
    query_pg()
