# ELT Project: Degustation Data Pipeline

This project provisions a PostgreSQL server on Azure, loads raw data using Python, and transforms it using dbt into a cleaned, analytics-ready table.

---

## Overview

This ELT pipeline includes:

1. **Infrastructure provisioning** with Terraform (Azure PostgreSQL Flexible Server)
2. **Data loading** from a CSV file into the raw schema with a Python script
3. **Data transformation** using dbt to build a cleaned table with degustation information

---

## Technologies Used

- **Azure** (PostgreSQL Flexible Server)
- **Terraform** for IaC
- **Python (pandas, sqlalchemy)** for raw data loading
- **dbt (Data Build Tool)** for SQL-based transformations

---

## Project Structure


```
├── terraform/ # Terraform config for Azure infrastructure
│ ├── main.tf
│ ├── variables.tf
│ ├── outputs.tf
│ └── terraform_tfvars_template.txt
│
├── data/ # Raw data source
│   └── degustations.csv
│
├── scripts/ # Python scripts
│    └── load_raw_data.py
│
├── dbt/ # dbt project directory
| └── dbt_activities
│    ├── models/
|        ├── activities
|        |    ├── schema.yml
|        |    └── sources.yml
|        └── staging
|             └── stg_raw_degustation_data.sql
│
└── README.md
```


# Terraform Infrastructure

## Components

- Azure Resource group
- Azure Database for PostgreSQL flexible server

## Configuration

Copy `terraform_tfvars_template.txt` to `terraform.tfvars` and set required variables there.

## Getting Started

```
cd terraform
terraform init
terraform plan
terraform apply
```

## Data Load with Python

This script loads the CSV file into the PostgreSQL database:

```
python scripts/load_raw_data.py
```

Ensure your .env file or environment variables contain:

```
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
DB_NAME=
```

You must run this step after the PostgreSQL server is created.

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


# ELT Pipeline Architecture


                ┌────────────┐
                │  CSV File  │
                └────┬───────┘
                     │
                     ▼
                ┌──────────────────┐
                │ Python Script    │
                │ load_data.py     │
                └────┬─────────────┘
                     ▼
        ┌───────────────────────────────┐
        │ PostgreSQL - raw_tourism_data │  ◄── Loaded data
        └────────────┬──────────────────┘
                     ▼
                ┌──────────────┐
                │ dbt models   │  ◄── Cleans & transforms
                └────┬─────────┘
                     ▼
        ┌───────────────────────────────┐
        │ PostgreSQL - cleaned_offers   │  ◄── Final analytical model
        └───────────────────────────────┘
