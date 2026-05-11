import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from scripts.utils import determine_terraform_dir, load_terraform_outputs

load_dotenv()
# Load environment variables
DB_PROVIDER = os.environ.get("DB_PROVIDER")
AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID") if DB_PROVIDER == "azure" else None
AZURE_RESOURCE_GROUP_NAME = (
    os.environ.get("AZURE_RESOURCE_GROUP_NAME") if DB_PROVIDER == "azure" else None
)
VM_NAME = os.environ.get("VM_NAME") if DB_PROVIDER == "azure" else None
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = (
    "127.0.0.1" if DB_PROVIDER in ["local", "azure_tunnel"] else None
)  # for azure VM this is not needed, since we take connection string from terraform
DB_PORT = (
    os.environ.get("LOCAL_PORT", "5432")
    if DB_PROVIDER == "azure_tunnel"
    else os.environ.get("DB_PORT", "5432")
)
DB_NAME = os.environ.get("DB_NAME")


def get_engine() -> Engine:
    """
    Build a SQLAlchemy Engine from environment variables.
    """
    if DB_PROVIDER == "azure":
        # get connection string from terraform outputs
        tf_dir = determine_terraform_dir()
        outputs = load_terraform_outputs(tf_dir)

        try:
            connection_string = outputs["postgres_example_conn_str"]["value"]
        except KeyError as missing:
            sys.exit(f"[fatal] missing key in terraform outputs: {missing}")

    elif DB_PROVIDER in ["local", "azure_tunnel"]:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        sys.exit(f"[fatal] provider type is not supported: {DB_PROVIDER}")

    return create_engine(connection_string)
