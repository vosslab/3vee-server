# SQLite migration plan

## Goals
- Provide a clear, staged path to add SQLite support alongside MariaDB.
- Keep the current MariaDB path working during the transition.
- Start with Python-only support; decide later whether to migrate PHP.

## Scope and assumptions
- Current storage uses Sinedon + MariaDB with MySQL-specific SQL and drivers.
- PHP pages read job metadata from the same MariaDB tables.
- SQLite support should be optional and selectable per environment.

## Non-goals
- A full ORM rewrite.
- Dropping MariaDB support.
- Feature parity for all legacy Sinedon tools on day one.

## Decision points
- Should SQLite be Python-only (local/dev) or also replace MariaDB for PHP?
- Should we keep a single schema compatible with both engines, or maintain two?
- Do we need read/write concurrency across multiple jobs in one SQLite file?

## Proposed phases

### Phase 0: discovery and design
- Inventory MySQL-specific SQL in `py/sinedon` (DDL, DML, functions).
- Identify tables written by Python and read by PHP.
- Define a minimal SQLite schema and compatibility rules.
- Decide on SQLite file location (for example `output/threev.sqlite`).

### Phase 1: Python-only SQLite (dev/local)
- Add a SQLite backend in Sinedon:
  - New module (for example `py/sinedon/sqlite_db.py`) that mirrors `sqldb.py`.
  - Connection handling via `sqlite3`, with row factory to match dict cursors.
  - SQL quoting helpers and type adapters.
- Update Sinedon config parsing to accept:
  - `engine = sqlite`
  - `path = /path/to/db.sqlite`
- Implement a schema initializer for SQLite:
  - Reuse existing table definitions but translate MySQL-only features:
    - `AUTO_INCREMENT` -> `INTEGER PRIMARY KEY AUTOINCREMENT`
    - `ENGINE=...` -> remove
    - `DEFAULT CURRENT_TIMESTAMP` -> `DEFAULT (CURRENT_TIMESTAMP)`
    - `UNSIGNED` -> remove (or validate in app)
- Add a small compatibility layer in `sqlexpr.py` to emit engine-specific SQL.
- Add a feature flag for runtime selection:
  - `THREEV_DB_ENGINE=sqlite` or config file override.
- Keep PHP on MariaDB during this phase.

### Phase 2: Robust SQLite support (prod-ready)
- Extend `dbupgrade.py` to handle SQLite schema upgrades.
- Create a migration mechanism for SQLite (simple version table + DDL scripts).
- Add concurrency guidance:
  - Enable WAL mode and `busy_timeout`.
  - Document limits for concurrent writers.
- Add smoke tests:
  - Create DB, insert a run, read it back.
  - Run one full job and verify results page uses stored metadata.
- Document operational guidance and limitations.

### Phase 3: PHP SQLite support (optional)
- Add SQLite support in PHP data layer (likely `php/inc/threevdata.inc`).
- Add PHP config flag to pick SQLite vs MariaDB.
- Update compose/entrypoint to optionally skip MariaDB.
- Validate end-to-end: submit job, view results, reload history.

## Key work items (detailed)
- Add SQLite connection and cursor wrapper matching MySQL dict cursor behavior.
- Add SQL dialect mapping in `sqlexpr.py` and/or a new `dialect.py`.
- Update `maketables.py` to emit SQLite-compatible DDL.
- Add a migration/version table (for example `schema_version`).
- Update `docs/CODE_ARCHITECTURE.md` and `docs/CONTAINER.md` with engine options.
- Add a rollback path: keep MariaDB config and schema intact.

## Risks and mitigations
- SQL dialect mismatch: keep MySQL as default, gate SQLite with a flag.
- Concurrency limits: use WAL and document single-writer expectations.
- PHP compatibility: defer until Python-only path is stable.
- Data migration: export/import via CSV for limited datasets.

## Estimated effort (ballpark)
- Phase 0: 1-2 days.
- Phase 1: 3-5 days (Python-only).
- Phase 2: 5-10 days (robust + tests + docs).
- Phase 3: 5-10 days (PHP + stack changes).

## Validation checklist
- `python3 -m py_compile` passes.
- `maketables.py` creates SQLite schema without errors.
- One end-to-end job stores run metadata and renders results.
- Results page loads historical data from SQLite (if PHP is updated).

## Rollback plan
- Keep MariaDB service in compose and config defaults untouched.
- Guard SQLite behind an env flag or config option.
- Provide a quick toggle back to MariaDB if issues arise.
