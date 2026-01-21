import json
import pathlib
import subprocess
import sys
from typing import Any


def determine_terraform_dir() -> pathlib.Path:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    tf_dir = (repo_root / "terraform").resolve()

    # Guardrails
    if not tf_dir.is_relative_to(repo_root):
        sys.exit(f"[fatal] terraform dir resolved outside repo: {tf_dir}")
    if not tf_dir.is_dir():
        sys.exit(f"[fatal] {tf_dir} does not exist")
    return tf_dir


def load_terraform_outputs(tf_dir: pathlib.Path) -> dict[str, Any]:
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
