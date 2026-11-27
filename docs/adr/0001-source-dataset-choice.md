# ADR-001: Choice of source dataset

- **Status:** Accepted
- **Date:** 2026-11-27
- **Decision owner:** Anna

## Context

The pipeline was built around the Pays de la Loire open data dataset
*Offre touristique : Lieux de dégustations (tous produits) en Pays de la Loire*. That dataset is no longer available on
data.paysdelaloire.fr, so the pipeline has no live source.

The project is meant to:

- show a production-style ELT pipeline (Python ingestion, dbt, Dagster, Terraform)
- run against a source that is updated regularly, so incremental loading,
  deduplication and auditing make sense
- extend to other tourist activities later

The name "degustation" is used in several places: the README title, the
dbt model names, the asset names and the docs. The repository and the dbt
project are already named generically (`activities-etl-project`,
`dbt_activities`).

## Decision drivers

1. **Source availability:** the source must be public and still maintained.
2. **Showcase value:** the data should exercise the existing features
   (raw → staging → current-state table, business key, audit, deduplication).
3. **Effort:** keep as much of the existing code and models as possible.
4. **Extensibility:** adding another dataset later should not require a rewrite.

## Options considered

### Option A: Keep degustations, using a frozen local snapshot

Keep the last downloaded CSV in `data/` and treat it as a static source.

- ✅ No changes to models or naming
- ❌ The source is dead, so incremental loading, the current-state table and
  audits only ever run on the same file
- ❌ A reviewer clicking the README link finds a dataset that no longer exists

### Option B: Switch to *Activités touristiques* (activities)

Replace the source with the regional activities dataset.

- ✅ Live, maintained source
- ❌ The source schema must be checked column by column *(to verify: date
  fields, identifier, packed multi-value fields)*

### Option C: Generic "tourist offer" ingestion, activities first

Same as B, but make the source dataset a configuration parameter (dataset id,
file name, source system), so that other regional tourism datasets can be
added later as new sources.

- ✅ Delivers the extensibility
- ❌ More effort up front (configuration, one staging model per source or a
  shared model)
- ❌ Risk of over-engineering if no second source is ever added

## Decision

*Proposed:* **Option B now, written so that Option C stays possible.**

- Use *Activités touristiques* as the single source.
- Rename "degustation" to generic names (`activity`), in line with
  the existing `activities-etl-project` and `dbt_activities` names.
- Keep dataset-specific values (dataset id, URL, file name) in one
  configuration place, but don't build a multi-source framework yet.
- Do not keep the degustation CSV in the repository (see ADR-002 on source
  data in the repository).

## Consequences

### Positive
- The pipeline runs on live data again, and the README link works.
- Incremental loading, the current-state table and the audit table get
  meaningful runs.
- Generic naming removes the mismatch between the repository name and its content.

### Negative / costs
- Renaming touches dbt models, Dagster assets, the README and the docs.
- The data model section of the README must be rewritten for events.
- Test fixtures must be rewritten to the activities schema. The degustation
  column layout is no longer used anywhere, including tests (see ADR-002).

### Follow-ups
- [x] Check the activities dataset schema and its update frequency
- [x] Decide the business key for an activity
- [x] Rename models and assets, and update the README
- [ ] Rewrite test fixtures to the activities schema
- [x] Add a CHANGELOG entry under `Changed` (source switch) and `Removed`
  (degustation source)

## References

- Regional open data portal: https://data.paysdelaloire.fr/
- Former source (no longer available): `234400034_070-010_offre-touristique-degustations-rpdl`
- Events dataset: *https://data.paysdelaloire.fr/explore/dataset/234400034_070-011_offre-touristique-activites-rpdl/information/*
