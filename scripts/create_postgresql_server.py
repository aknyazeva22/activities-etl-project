import os
import pathlib
import subprocess
from typing import List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TERRAFORM_DIR = pathlib.Path(__file__).parents[1] / "terraform"
STATE_FILE    = "terraform.tfvars"

AZURE_SUBSCRIPTION_ID = os.environ['AZURE_SUBSCRIPTION_ID']
AZURE_RESOURCE_GROUP_NAME = os.environ['AZURE_RESOURCE_GROUP_NAME']
AZURE_LOCATION = os.environ['AZURE_LOCATION']
POSTRES_SERVER_NAME = os.environ['POSTRES_SERVER_NAME']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

# Format terraform config
TERRAFORM_CONF = f"""
subscription_id = "{AZURE_SUBSCRIPTION_ID}"
resource_group_name = "{AZURE_RESOURCE_GROUP_NAME}"
location = "{AZURE_LOCATION}"
postgres_server_name = "{POSTRES_SERVER_NAME}"
db_admin = "{DB_USER}"
db_password = "{DB_PASSWORD}"
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
