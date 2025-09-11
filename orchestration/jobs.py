import os
import time
import runpy
import socket
import subprocess
from dagster import op, job, SkipReason
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from orchestration.resources.bastion_tunnel import BastionTunnelResource


load_dotenv()

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_HOST = "127.0.0.1"
DB_PORT = os.environ.get('DB_PORT', '5432')  # port on VM
LOCAL_PORT = os.environ.get('DB_PORT', '5432')  # port on localhost for tunnel

BASTION_NAME = os.environ.get('BASTION_NAME', 'bastion-host')

# Infrastructure
@op
def create_azure_psql_server():
    runpy.run_module("scripts.create_postgresql_server", run_name="__main__")

@job
def provision_infra():
    create_azure_psql_server()

# Tunnel
def wait_for_port(host, port, timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with socket.socket() as s:
            if s.connect_ex((host, port)) == 0:
                return
        time.sleep(0.25)
    raise RuntimeError(f"Port {port} on {host} did not open in time")

@op(config_schema={"port": int})
def start_tunnel_op(context):
    # if not in azure_tunnel mode, skip
    mode = os.getenv("DB_PROVIDER", "local")
    if mode != "azure_tunnel":
        raise SkipReason(f"Skipping tunnel because MODE={mode}")
    
    port = context.op_config["port"]  # port could be set in dagster UI
    tunnel_envs = {
        **os.environ,
        "NAME": str(BASTION_NAME),
        "RESOURCE_PORT": str(DB_PORT),
        "LOCAL_PORT": str(port),
    }
    try:
        completed = subprocess.run(
            ["scripts/tunnelctl.sh","start"],
            env=tunnel_envs,
            check=True,
            capture_output=True,
            text=True,
        )
        context.log.info(f"tunnelctl stdout:\n{completed.stdout.strip()}")
        if completed.stderr.strip():
            context.log.warning(f"tunnelctl stderr:\n{completed.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        context.log.error(
            "tunnelctl failed "
            f"(exit {e.returncode})\n"
            f"cmd: {' '.join(e.cmd) if isinstance(e.cmd, list) else e.cmd}\n"
            f"stdout:\n{(e.stdout or '').strip()}\n"
            f"stderr:\n{(e.stderr or '').strip()}"
        )
        # Re-raise so the op fails clearly
        raise

    wait_for_port("127.0.0.1", port, timeout=60)
    context.log.info(f"Bastion tunnel UP on 127.0.0.1:{port}")

@op(config_schema={"port": int})
def assert_tunnel_op(context):
    # if not in azure_tunnel mode, skip
    mode = os.getenv("DB_PROVIDER", "local")
    if mode != "azure_tunnel":
        raise SkipReason(f"Skipping tunnel because MODE={mode}")
    
    port = context.op_config["port"]  # port could be set in dagster UI
    try:
        wait_for_port("127.0.0.1", port, timeout=3)
        context.log.info(f"Tunnel healthy on 127.0.0.1:{port}")
    except Exception:
        raise RuntimeError("Tunnel not running. Start it first.")

@op
def stop_tunnel_op(_):
    # if not in azure_tunnel mode, skip
    mode = os.getenv("DB_PROVIDER", "local")
    if mode != "azure_tunnel":
        raise SkipReason(f"Skipping tunnel because MODE={mode}")

    subprocess.run(["scripts/tunnelctl.sh","stop"], check=True, capture_output=True, text=True)


@job
def start_tunnel():
    start_tunnel_op()

@job
def assert_tunnel():
    assert_tunnel_op()

@job
def stop_tunnel():
    stop_tunnel_op()