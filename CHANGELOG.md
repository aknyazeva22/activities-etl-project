# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versions 0.1.0 to 0.6.0 were reconstructed from git history.

## [Unreleased]

### Changed
- dbt macros renamed (`75dfe3d`)
- dbt project reorganised: `staging/paysdelaloire/` and `intermediate/` layers, dbt naming conventions (`stg_<source>__<entity>`, `int_...`), yml files next to their models (`3302d19`, `75dfe3d`)
- The current-state table moved from staging to the intermediate layer (`int_activities__current`) (`3302d19`)

### Fixed
- Folder config in `dbt_project.yml` pointed to a non-existent project and was ignored (`3302d19`)
- Filter on contact details had wrong operator precedence (`not a or b ...`) (`3302d19`)
- `is_address_given` was true only when all four address lines were filled (`3302d19`)
- Helper columns (`*_norm`, `row_num`) no longer leak into model outputs (`3302d19`)
- Test on `guided_group_visit_on_request` was never run (missing `tests:` key) (`3302d19`)
- Documentation used `code_postal` instead of `postal_code` (`3302d19`)

### Removed
- Documentation for the non-existent `activities_raw` model (`3302d19`)

## [0.7.0] - 2026-11-27 — Architecture Decision Records and ingestion review

### Added
- Architecture Decision Records: ADR-001 (choice of source dataset) and ADR-002 (source data in the repository and test fixtures) in docs/adr/ (`992b400`)
- Ingestion run audit table, created via migrations (`0f9e468`)
- Audit records pushed to the audit table on each raw data ingest (`f1ed034`, `c2a36df`, `b10bd7c`)
- Dedicated audit error for empty input files (`a530b9e`)
- Custom exceptions for raw data loading, with error logging (`a7d95a7`, `f556c82`)
- Unit tests for raw data loading (`ae17250`, `269da91`)

### Changed
- Audit record modelled as a dataclass (`d28bf23`)
- Audit table name and schema are now parameters (`05c0f9c`)
- PostgreSQL schema creation handled in a single place (`b0b231b`)
- Exceptions and dataclasses moved to separate modules (`3e64bec`)
- Reviewed `.gitignore` (`d650dfb`)

### Fixed
- Index error when writing to the audit table (`1bde1f4`)

## [0.6.0] - 2026-06-05 — Deduplication and current-state staging

### Added
- Staging "current" table holding the latest version of each activity (`e776e1d`)

### Changed
- `activity_key` redefined as a best-effort business key (`6bc0d4d`)
- Removed the primary key on `activity_key` from the first staging table (`502d13c`)
- README project tree simplified and updated with new directories (`22d3de0`, `7b48920`)

### Fixed
- Duplicates coming from the source during raw data loading (`db25622`)

## [0.5.0] - 2026-01-29 — Code quality, tooling and CI

### Added
- Technical metadata columns in the raw data layer (`2280cd4`)
- `uv` for Python dependency management, with `uv.lock` committed (`53d70d5`, `6c4f340`)
- `pre-commit` hooks with `ruff` (Python) and `sqlfluff` (SQL) (`7d37d09`, `271ed70`, `944c222`)
- Basic GitHub Actions CI pipeline, with dedicated dbt profiles for CI (`e7f451c`, `42873b9`, `a24b287`)
- README sections on dbt configuration and technical setup (`c63e01c`, `f6d29c3`)

### Changed
- Refactored raw data loading and `ensure_pg_schema` (`9194d6e`, `5202826`, `687a2b6`, `ae85244`)
- `sqlfluff` skipped in CI for now (`df8f0c9`)

### Fixed
- "Primary key already exists" error (`0f97d92`)

## [0.4.0] - 2026-01-18 — Data modelling and staging layer

### Added
- Script to fetch source CSV files, with clearer asset naming and descriptions (`67b67c5`, `b2c41fc`, `63bdd97`)
- `activity_key` column in the dbt staging model, with tests (`f03ca25`, `b9989cf`)
- Primary key on the staging table (`375f174`)
- `dbt_utils` dependency and custom dbt macros (`26f244e`, `6038c40`)
- README: motivation, use cases and data model (`07c73c7`, `6cd4684`)

### Changed
- Raw data load switched from append to replace (full refresh) (`e81b5e6`)
- Staging model materialised as a table instead of a view (`6a312b0`)
- Activities with no contact data are excluded at staging (`bea10f6`)
- Renamed the dbt staging model (`e6bdd3a`, `20aeac8`)

### Fixed
- Code cleanup after renaming, typo and README naming fixes (`679f09f`, `f97e15e`, `a03e9da`)

## [0.3.0] - 2025-09-16 — Multiple infrastructure modes (local / Azure VM / Azure Bastion)

### Added
- Local PostgreSQL option with Docker Compose (`c4f7e24`, `8aaf38f`)
- Azure VM hosting PostgreSQL, provisioned with Terraform (`b93efb1`, `2739f6f`, `1d6bcda`)
- Utilities to read Terraform outputs (host, port, connection string) (`ad3a66e`, `b3bc7ea`, `68ffd19`)
- Azure Bastion with an SSH tunnel script and an `azure_tunnel` mode in `.env` (`2785f6c`, `fd326e6`, `8d24867`, `1d6bcda`)
- SQL schema as a parameter, created if it does not exist (`b4db1c2`, `a16cc6b`)
- README documenting the three infrastructure modes (`348be5d`)

### Changed
- dbt source uses a dynamic schema; fixed the dbt project directory (`a00606e`)
- Updated `.env` template (`e1d61f9`)

### Fixed
- No error raised when the mode is not `azure_tunnel` (`bbf65fd`)

## [0.2.0] - 2025-08-14 — Orchestration with Dagster

### Added
- Dagster orchestration of the pipeline (`3976d85`)
- Terraform run as a Dagster job (`6840ecf`, `9ca7485`)
- dbt integrated in Dagster, with dbt profiles generated by Dagster (`11a52c6`, `86bb4cb`)
- `compute_kind` set on assets (`0a09d87`)
- Structured documentation (`7fee1f4`, `05a0915`)

## [0.1.0] - 2025-07-02 — Initial pipeline

### Added
- Terraform configuration (`24e8306`)
- Python script to load raw data into PostgreSQL (`c237d5c`)
- dbt project, with profiles generated from Terraform state (`3b36321`, `33f3ddf`)
- `is_address_given` field (`c1e10e2`)
- Documentation of the dbt configuration and file tree (`49e6c77`, `4acc8c9`)
