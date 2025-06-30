import sys
import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]  # go to the root dir
tf_dir    = (REPO_ROOT / "terraform").resolve()

if not tf_dir.is_relative_to(REPO_ROOT):
    sys.exit(f"[fatal] terraform dir resolved outside repo: {tf_dir}")

if not tf_dir.is_dir():
    sys.exit(f"[fatal] {tf_dir} does not exist")

# Get Terraform outputs as JSON
raw = subprocess.check_output(
    ["terraform", "output", "-json"],
    cwd=tf_dir,
    text=True
)
outputs = json.loads(raw)

# Extract values
host = outputs['db_host']['value']
user = outputs['db_user']['value']
password = outputs['db_password']['value']
dbname = outputs['db_name']['value']

# Format dbt profile
profile = f"""
dbt_activities:
  target: dev
  outputs:
    dev:
      type: postgres
      host: {host}
      user: {user}
      password: {password}
      port: 5432
      dbname: {dbname}
      schema: public
      threads: 1
"""

# Write to profiles.yml
profiles_dir = pathlib.Path('./dbt/dbt_activities')
profiles_dir.mkdir(exist_ok=True)
(profiles_dir / 'profiles.yml').write_text(profile.strip())

print("dbt profiles.yml generated.")
