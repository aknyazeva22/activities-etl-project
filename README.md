# ELT Project: Degustation Data Pipeline

This project provisions a PostgreSQL server on Azure, loads raw data using Python, and transforms it using dbt into a cleaned, analytics-ready table.

---

## Overview

This ELT pipeline includes:

1. **Infrastructure provisioning** with Terraform (Azure PostgreSQL Flexible Server)
2. **Data loading** from a CSV file into the raw schema with a Python script
3. **Data transformation** using dbt to build a cleaned table with degustation information
4. **Pipeline orchestration** with Dagster

---

## Technologies Used

- **Azure** (PostgreSQL Flexible Server)
- **Terraform** for IaC
- **Python (pandas, sqlalchemy)** for raw data loading
- **dbt (Data Build Tool)** for SQL-based transformations
- **Dagster** for orchestration and observability

---

## Project Structure


```
├── data/ # Raw data source
│   └── degustations.csv
├── orchestration # Dagster configuration
│   ├── assets.py
│   ├── definitions.py
│   └── jobs.py
├── dbt/ # dbt project directory
| └── dbt_activities
│    └── models/
|        ├── activities
|        |    ├── schema.yml
|        |    └── sources.yml
|        └── staging
|             └── stg_raw_degustation_data.sql
├── pyproject.toml
├── README.md
├── scripts/ # Python scripts
│    ├── create_postgresql_server.py
│    ├── generate_profiles.py
│    └── load_raw_data.py
├── setup.py
└── terraform/ # Terraform config for Azure infrastructure
     ├── main.tf
     ├── outputs.tf
     ├── terraform_tfvars_template.txt
     └── variables.tf
```

# Getting Started

## Clone & bootstrap

```
git clone https://github.com/aknyazeva22/activities-etl-project.git
cd activities-etl-project
cp env.template .env  # fill in secrets
```

## Connect to Azure

Before working with this repository, make sure you are authenticated to your Azure account.

Open a terminal or command prompt.

Run the following command:

```
az login
```

A browser window will open prompting you to sign in with your Azure credentials. Follow the on-screen instructions.

If you have multiple subscriptions, you can set the active subscription after logging in using:

```
az account set --subscription "<subscription-name-or-id>"
```

Important: Also add your <subscription-name-or-id> to the .env file in this repository so that other tools and scripts can reference it.

You must have the Azure CLI installed. If not, see [Install the Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) before proceeding.

## Launch Dagster

```
dagster dev
```

## Run the provision_infra job

In the Dagster UI, select **Jobs -> `provision_infra` -> Launch**

Or headless

```
dagster job execute -f dagster/jobs.py -j provision_infra
```

That single run will:

1. `terraform init / plan / apply` to spin up Azure PostgreSQL
2. Make connection details available to downstream ops (dbt, Python ETL, etc.)


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
