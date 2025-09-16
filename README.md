# ELT Project: Degustation Data Pipeline

This project provisions a PostgreSQL server and builds a complete ELT pipeline:  
- **Extract/Load**: raw data is ingested using Python.  
- **Transform**: data is modeled and cleaned with dbt into analytics-ready tables.  

The infrastructure can be set up in three modes:  
- **local** – PostgreSQL running in a Docker container (via `docker compose`)  
- **azure** – PostgreSQL provisioned directly on an Azure VM  
- **azure_tunnel** – PostgreSQL on an Azure VM accessed securely through an Azure Bastion tunnel (provisioned with Terraform)

---

## Overview

This ELT pipeline includes:

1. **Infrastructure provisioning**  
   - On Azure (`azure`, `azure_tunnel`) with Terraform  
   - Locally (`local`) with a setup script

2. **Data loading** from a CSV file into the raw schema with a Python script

3. **Data transformation** using dbt to build a cleaned table with degustation information

4. **Pipeline orchestration** with Dagster

---

## Technologies Used

- **PostgreSQL** as the target database:
  - **Option 1 (Cloud – azure):** VM with a PostgreSQL Server, provisioned via Terraform  
  - **Option 2 (Cloud – azure_tunnel):** VM with a PostgreSQL Server, accessed through Azure Bastion, provisioned via Terraform  
  - **Option 3 (Local – local):** PostgreSQL in Docker for local development without cloud resources  

- **Terraform** for infrastructure provisioning (`azure`, `azure_tunnel`)  
- **Python (pandas, sqlalchemy)** for raw data loading  
- **dbt (Data Build Tool)** for SQL-based transformations  
- **Dagster** for orchestration and observability

---

## Choose Your Deployment Mode

This project supports three modes depending on your environment and needs:

1. **Azure (Cloud – `azure`)**  
   Provisions a PostgreSQL server on an Azure VM using Terraform.  
   Best suited for production or shared team environments.  
   Requires an active Azure subscription and credentials configured via `az login`.  
   Add to your `.env` file: `DB_PROVIDER=azure`


2. **Azure with Bastion Tunnel (Cloud – `azure_tunnel`)**  
    Provisions a PostgreSQL server on an Azure VM and connects through an Azure Bastion tunnel, managed by Terraform.  
    Useful when direct access to the VM is restricted or must be secured via tunneling.  
    Requires an active Azure subscription and credentials configured via `az login`.  
    Add to your `.env` file: `DB_PROVIDER=azure_tunnel`


3. **Local Development (Docker – `local`)**  
    Spins up a PostgreSQL instance inside a Docker container.  
    Ideal for development, testing, or cost-free experimentation.  
    Requires Docker and Docker Compose installed locally.  
    Add to your `.env` file: `DB_PROVIDER=local`


All modes are fully compatible with the rest of the stack (Python ingestion, dbt transformations, Dagster orchestration).  
You can switch between them by updating `DB_PROVIDER` in your `.env` file.

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
|    ├── download_degustation_csv.py
│    ├── generate_profiles.py
│    ├── load_raw_data.py
|    ├── tunnelctl.sh
│    └── utils.py
├── setup.py
├──terraform/ # Terraform config for Azure infrastructure (azure mode)
│    ├── cloud-init-postgres.yml
│    ├── main.tf
│    ├── nic.tf
│    ├── outputs.tf
│    ├── terraform.tfvars.template
│    └── variables.tf
└── terraform/ # Terraform config for Azure infrastructure (azure mode)
     ├── cloud-init-postgres.yml
     ├── main.tf
     ├── nic.tf
     ├── outputs.tf
     ├── terraform.tfvars.template
     └── variables.tf
```

# Getting Started

## Clone & bootstrap

```
git clone https://github.com/aknyazeva22/activities-etl-project.git
cd activities-etl-project
cp env.template .env  # fill in secrets and choose DB_PROVIDER (azure, azure_tunnel, or local)
```

The provided `env.template` file lists all required environment variables. Use it as a guide when filling in your `.env`.


## Connect to Azure (Cloud)

For `azure` and `azure_tunnel` modes, you must be authenticated to your Azure account.

1. Open a terminal or command prompt.  
2. Run the following command:

```
az login
```

A browser window will open prompting you to sign in with your Azure credentials. Follow the on-screen instructions.

If you have multiple subscriptions, set the active subscription after logging in:

```
az account set --subscription "<subscription-name-or-id>"
```

Important: Also add your <subscription-name-or-id> to the .env file in this repository so that other tools and scripts can reference it.

You must have the Azure CLI installed. If not, see [Install the Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) before proceeding.

## Run PostgreSQL Locally (Docker – `local`)

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

## Run Infrastructure Jobs

### Provision Infrastructure (azure, azure_tunnel)

In the Dagster UI, select **Jobs -> `provision_infra` -> Launch**

Or headless

```
dagster job execute -f dagster/jobs.py -j provision_infra
```

That single run will:

1. Run terraform init / plan / apply to spin up a PostgreSQL server on an Azure VM

2. Make connection details available to downstream ops (dbt, Python ETL, etc.)

This job is not applicable in local mode (where PostgreSQL runs in Docker).

### Tunnel Management (azure_tunnel only)

For azure_tunnel mode, additional jobs manage the Bastion tunnel.
If launched in other modes, these jobs will simply log a “skipped” message.

* start_tunnel – opens the Bastion tunnel
* assert_tunnel – checks if the tunnel is up
* stop_tunnel – closes the tunnel


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
