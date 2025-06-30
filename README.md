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

dbt models take raw data from the `public.raw_degustation_data` table and create a cleaned, structured table for analysis.

```

cd dbt/dbt_activities
dbt init  # you could write dbt profile with connection data here
dbt run   # runs transformations
dbt test  # runs data quality checks
```

Make sure profiles.yml points to your Azure PostgreSQL instance.


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
