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

- **PostgreSQL** as the target database:
  - **Option 1 (Cloud): Azure PostgreSQL Flexible Server**, provisioned via Terraform (Infrastructure as Code)
  - **Option 2 (Docker): PostgreSQL in Docker**, for local development without cloud resources
- **Terraform** for infrastructure provisioning (Azure option)
- **Python (pandas, sqlalchemy)** for raw data loading
- **dbt (Data Build Tool)** for SQL-based transformations
- **Dagster** for orchestration and observability

---

## Choose Your Deployment Mode

This project supports two modes depending on your environment and needs:

1. Azure + Terraform (Cloud)

Provisions a PostgreSQL Flexible Server on Azure using Terraform.

Best suited for production or team environments.

Requires an active Azure subscription and credentials configured via az login.

Add to your .env file `DB_PROVIDER=azure`

2. Local Development (Docker)

Spins up a PostgreSQL instance inside a Docker container.

Ideal for development, testing, or cost-free experimentation.

Requires only Docker and Docker Compose installed locally.

Add to your .env file `DB_PROVIDER=local`


Both modes are fully compatible with the rest of the stack (Python ingestion, dbt transformations, Dagster orchestration). You can switch between them by updating DB_PROVIDER in your .env file.

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
├── docker-compose.yml # Docker config for local PostgreSQL
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

## Connect to Azure (Cloud)

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

## Run Docker (Docker)

If you prefer to use a local PostgreSQL instance instead of Azure, you can launch it with Docker.

1. Make sure you have **Docker** and **Docker Compose** installed.
2. Configure your .env file with the required variables. You need to set these variables:

```
DB_PROVIDER=local
DB_USER=<username>
DB_PASSWORD=<password>
DB_NAME=<database_name>
DB_PORT=<port>
PGDATA_DIR=<host_directory>   # e.g., /var/lib/postgresql/data
```

`PGDATA_DIR` is the directory on your local filesystem where Postgres data will be stored persistently.


3. Start the container:
```
docker compose up -d
```
4. Verify that PostgreSQL is running:
```
docker ps
```
You should see a container whose name includes **postgres** (e.g., projectname-postgres-1).

5. Connect to the database (optional):
```
psql -h localhost -U $DB_USER -d $DB_NAME -p $DB_PORT
```

The password will be the value of `DB_PASSWORD` from your .env file.


6. To stop the container:
```
docker compose down
```

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
