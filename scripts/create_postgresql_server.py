import pathlib
import subprocess
from typing import List
from pathlib import Path
from os import environ
from dotenv import load_dotenv

load_dotenv()

TERRAFORM_DIR = pathlib.Path(__file__).parents[1] / "terraform"
STATE_FILE    = "terraform.tfvars"

# Format terraform config
TERRAFORM_CONF = f"""
allowed_db_cidr = "{environ['ALLOWED_IP']}"
db_admin = "{environ['DB_USER']}"
db_name = "{environ['DB_NAME']}"
db_password = "{environ['DB_PASSWORD']}"
db_port = "{environ['DB_PORT']}"
host_admin = "{environ['HOST_ADMIN']}"
location = "{environ['AZURE_LOCATION']}"
pgdata = "{environ['PGDATA_DIR']}"
postgres_server_name = "{environ['POSTRES_SERVER_NAME']}"
postgres_version = "{environ['POSTGRES_VERSION']}"
resource_group_name = "{environ['AZURE_RESOURCE_GROUP_NAME']}"
ssh_public_key_path = "{environ['SSH_KEY_PATH']}"
subscription_id = "{environ['AZURE_SUBSCRIPTION_ID']}"
vm_name = "{environ['VM_NAME']}"
vnet_cidr = "{environ['VNET_CIDR']}"
"""

def _tf(cmd: List[str]) -> None:
    """
    Run a Terraform CLI command with the working directory set to TERRAFORM_DIR.
    """
    subprocess.run(["terraform", *cmd], cwd=TERRAFORM_DIR, check=True)

def write_tfvars(config: str, path: Path) -> None:
    """
    Write the Terraform variable configuration to a file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config.strip() + "\n", encoding="utf-8")

def apply_tf() -> None:
    """
    Initialize and apply the Terraform configuration.
    """
    _tf(["init"])
    _tf(["apply", "-auto-approve"])


if __name__ == "__main__":
    tfvars_path = TERRAFORM_DIR / STATE_FILE
    write_tfvars(TERRAFORM_CONF, tfvars_path)
    apply_tf()
