# ADR-002: Source data in the repository and test fixtures

- **Status:** Accepted
- **Date:** 2026-11-25
- **Decision owner:** Anna
- **Related:** [ADR-001: Choice of source dataset](0001-source-dataset-choice.md)

## Context

The pipeline was first developed and tested against the degustation dataset (*Offre touristique – Dégustations*, Pays de la Loire open data). A copy of that CSV was kept in `data/` and used to develop and test the raw data loader.

Several facts make this a problem:

- The dataset contains **contact details of businesses and their owners** (names, phone numbers, emails, addresses). Some of these identify individual people, so they count as personal data even though they were published as open data.
- The original dataset **no longer exists** (ADR-001), so a stored copy cannot be refreshed, and the people in it can no longer update or remove their information at the source.
- The tests need data that is **stable, small and covers edge cases**. A real extract is large and may not contain the cases the code handles (duplicates, missing contact data, empty addresses, packed values).

## Decision drivers

1. **Privacy:** no personal data in a public repository.
2. **Test quality:** fixtures must cover every behaviour the pipeline handles.
3. **Determinism:** tests must give the same result on every run and in CI.
4. **Source independence:** fixtures should keep working when the source changes (degustations → activities, ADR-001).
5. **Effort:** fixtures should be quick to write and easy to read.

## Options considered

### Option A: Keep a real degustation extract as test data

- ✅ Realistic values and formats
- ❌ Personal data in a public repository
- ❌ Unlikely to cover all edge cases; large and hard to read in a test

### Option B: Anonymise or pseudonymise the real extract

Replace names, emails and phone numbers in the real file.

- ✅ Keeps realistic structure and value distributions
- ❌ Pseudonymised data is still personal data under GDPR. Real anonymisation is hard to prove: addresses, communes and business
  descriptions can still identify a person.
- ❌ Needs a repeatable anonymisation script, and someone has to check every run

### Option C: Hand-written synthetic fixtures

A small CSV (about 10 rows) that follows the source column layout, with invented values, one row per behaviour to test.

- ✅ No personal data
- ✅ Each row has a purpose; tests stay readable
- ✅ Deterministic and small
- ❌ Less realistic value distributions
- ❌ Must be updated by hand when the source schema changes

### Option D: Generated synthetic data (Faker with a fixed seed)

- ✅ Any volume; useful for performance or volume tests
- ✅ Deterministic with a fixed seed
- ❌ Less readable than hand-written rows
- ❌ Some Faker functions produce real-looking emails or phone numbers, so generation must be restricted

### Option E: Download live data during the tests

- ✅ Always the current schema
- ❌ Not deterministic; tests depend on the network and on a third party
- ❌ Brings real personal data into CI logs and artefacts

## Decision

**No source data is committed to the repository. Tests use synthetic data only: hand-written fixtures (Option C) by default, generated data
(Option D) only where a test needs volume.**

Rules:

1. `data/` is ignored by git, except `data/README.md`. Source data is fetched at runtime by the fetch script.
2. A pre-commit hook refuses data files in `data/`. A second hook scans
   `tests/`, `docs/` and the README for real-looking emails and phone numbers.
3. Fixtures live in `tests/fixtures/` and follow the **column layout** of the source, keeping only the columns the code uses. They contain no real values:
   - emails on reserved domains (`example.com`, `example.org`, `example.net`)
   - phone numbers with one fixed fictional prefix
   - invented names and identifiers with a visible pattern (`TEST-0001`)
   - real commune names are allowed; street addresses are invented
4. Each fixture row covers one documented behaviour (duplicates, the current-state table, missing contact data, empty addresses, packed values, encoding, empty file).
5. The column layout is defined in one place, so a source change only needs one update.
6. dbt logic is tested with dbt unit tests on synthetic input rows, not on loaded real data.
7. Examples in the documentation use synthetic values only.

## Consequences

### Positive
- No personal data in the repository, its history or CI.
- Tests are small, fast and deterministic, and they document the expected behaviour row by row.
- Switching the source (ADR-001) means updating the fixture columns, not replacing a large data file.
- Clear separation: real data exists only in runtime environments (local database, Azure VM), never in the code.

### Negative / costs
- Fixtures can drift from the real source schema. A schema change will only show up when the pipeline runs on real data. Mitigation: a schema check at ingestion that fails on missing or unexpected columns (possible future work).
- Writing fixtures by hand takes time, and each new behaviour needs a new row.
- Value-level surprises in the real data (formats, rare values) are not covered by unit tests.

### Follow-ups
- [ ] Add `.gitignore` rules and both pre-commit hooks
- [ ] Create `tests/fixtures/` with the sample and empty CSV files and a README
- [ ] Rewrite the raw data loading tests to use the fixtures
- [ ] Add dbt unit tests for the staging logic
- [ ] Run pre-commit and the tests in CI
- [ ] Consider a schema check at ingestion (possible ADR-003)

## References

- GDPR, Recital 26: pseudonymised data remains personal data
- dbt unit tests: https://docs.getdbt.com/docs/build/unit-tests
