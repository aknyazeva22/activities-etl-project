## Data Transformation with dbt

This section covers how to configure and run dbt models. The goal is to take raw data from the `public.raw_degustation_data` table and create a cleaned, structured view.

## Configure dbt

Before running dbt, you need a `profiles.yml` file that defines your database connection. You can create it in two ways:

### Option 1: Initialize with dbt

Run:

```
dbt init
```

Follow the prompts to set up your profile manually.

### Option 2: Generate Automatically from Terraform Output

You can generate the profiles.yml file automatically:

```
python scripts/generate_profiles.py
```

This script reads Terraform outputs and creates the necessary dbt configuration in `dbt/dbt_activities/profiles.yml`.

## 2. Run and Test dbt

Navigate to the dbt project directory:

```
cd dbt/dbt_activities
```

Then run the following commands:

```
dbt run   # executes the transformation models
dbt test  # runs data quality checks
```
