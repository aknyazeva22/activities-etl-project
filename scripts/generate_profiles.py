import json
import pathlib
import subprocess
import sys
from typing import Any, Dict


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

def build_profile(outputs: Dict[str, Any]) -> str:
    """Return the YAML string for dbt profiles.yml."""
    try:
        host = outputs["db_host"]["value"]
        port = outputs["db_port"]["value"]
        user = outputs["db_user"]["value"]
        password = outputs["db_password"]["value"]
        dbname = outputs["db_name"]["value"]
    except KeyError as missing:
        sys.exit(f"[fatal] missing key in terraform outputs: {missing}")

    return f"""dbt_activities:
  target: dev
  outputs:
    dev:
      type: postgres
      host: {host}
      user: {user}
      password: {password}
      port: {port}
      dbname: {dbname}
      schema: public
      threads: 1
""".lstrip()

def write_profile(yaml_text: str, profiles_dir: pathlib.Path) -> None:
    """Write the YAML string to profiles.yml, creating the directory if needed."""
    profiles_dir.mkdir(parents=True, exist_ok=True)
    path = profiles_dir / "profiles.yml"
    path.write_text(yaml_text)
    print(f"Wrote to {path}")

def main() -> None:
    repo_root = pathlib.Path(__file__).resolve().parents[1]  # adjust as needed
    tf_dir = (repo_root / "terraform").resolve()

    # Guardrails
    if not tf_dir.is_relative_to(repo_root):
        sys.exit(f"[fatal] terraform dir resolved outside repo: {tf_dir}")
    if not tf_dir.is_dir():
        sys.exit(f"[fatal] {tf_dir} does not exist")

    outputs = load_terraform_outputs(tf_dir)
    yaml_text = build_profile(outputs)
    write_profile(yaml_text, pathlib.Path("dbt/dbt_activities"))


if __name__ == "__main__":
    main()
