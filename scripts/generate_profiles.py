import os
import json
import pathlib
import subprocess
import sys
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

def load_terraform_outputs(tf_dir: pathlib.Path) -> Dict[str, Any]:
    """Run `terraform output -json` and return the parsed dict."""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=tf_dir,
            text=True,
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        sys.exit(f"[fatal] failed to run terraform: {exc}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"[fatal] terraform JSON was invalid: {exc}")

def profile_parameters_from_terraform(outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Return the dict with connection parameters for dbt profiles.yml
       from terraform outputs
    """
    parameters_dict = dict()
    try:
        parameters_dict["host"] = outputs["db_host"]["value"]
        parameters_dict["port"] = 5432
        parameters_dict["user"] = outputs["db_user"]["value"]
        parameters_dict["password"] = outputs["db_password"]["value"]
        parameters_dict["dbname"] = outputs["db_name"]["value"]
        parameters_dict["schema"] = "public"
    except KeyError as missing:
        sys.exit(f"[fatal] missing key in terraform outputs: {missing}")

    return parameters_dict

def profile_parameters_from_env() -> Dict[str, Any]:
    """Return the dict with connection parameters for dbt profiles.yml
       from environment variables
    """
    parameters_dict = dict()
    try:
        parameters_dict["host"] = "localhost"
        parameters_dict["port"] = os.environ.get('DB_PORT', '5432')
        parameters_dict["user"] = os.environ.get('DB_USER')
        parameters_dict["password"] = os.environ.get('DB_PASSWORD')
        parameters_dict["dbname"] = os.environ.get('DB_NAME')
        parameters_dict["schema"] = "public"
    except KeyError as missing:
        sys.exit(f"[fatal] missing key in .env: {missing}")

    return parameters_dict

def build_profile(parameters_dict: Dict[str, Any]) -> str:
    """Return the YAML string for dbt profiles.yml."""
    return f"""dbt_activities:
  target: dev
  outputs:
    dev:
      type: postgres
      host: {parameters_dict["host"]}
      user: {parameters_dict["user"]}
      password: {parameters_dict["password"]}
      port: {parameters_dict["port"]}
      dbname: {parameters_dict["dbname"]}
      schema: {parameters_dict["schema"]}
      threads: 1
""".lstrip()

def write_profile(yaml_text: str, profiles_dir: pathlib.Path) -> None:
    """Write the YAML string to profiles.yml, creating the directory if needed."""
    profiles_dir.mkdir(parents=True, exist_ok=True)
    path = profiles_dir / "profiles.yml"
    path.write_text(yaml_text)
    print(f"Wrote to {path}")

def main() -> None:
    db_provider = os.environ.get('DB_PROVIDER')
    if db_provider == "azure":
        parameters_dict = profile_parameters_from_terraform()


        repo_root = pathlib.Path(__file__).resolve().parents[1]  # adjust as needed
        tf_dir = (repo_root / "terraform").resolve()

        # Guardrails
        if not tf_dir.is_relative_to(repo_root):
            sys.exit(f"[fatal] terraform dir resolved outside repo: {tf_dir}")
        if not tf_dir.is_dir():
            sys.exit(f"[fatal] {tf_dir} does not exist")


        outputs = load_terraform_outputs(tf_dir)
        connection_parameters = profile_parameters_from_terraform(outputs)
    elif db_provider == "local":
        connection_parameters = profile_parameters_from_env()
    else:
        sys.exit(f"[fatal] provider type is not supported: {db_provider}")

    yaml_text = build_profile(connection_parameters)
    write_profile(yaml_text, pathlib.Path("dbt/dbt_activities"))


if __name__ == "__main__":
    main()
