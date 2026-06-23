## MODIFIED Requirements

### Requirement: SQLite database backend
The application SHALL use SQLite as its sole persistent database. All environments (development, staging, production) SHALL connect via `DATABASE_URL` with the `sqlite+aiosqlite` driver. PostgreSQL, Supabase, and pgvector SHALL NOT be supported.

#### Scenario: Default local database
- **WHEN** the backend starts without `DATABASE_URL` override
- **THEN** it connects to `sqlite+aiosqlite:///./wfrp_solo.db`
- **AND** creates or migrates schema as needed

#### Scenario: Custom SQLite path
- **WHEN** `DATABASE_URL` points to another sqlite file path
- **THEN** the backend uses that file for all persistence

#### Scenario: PostgreSQL profile rejected
- **WHEN** `DATABASE_URL` uses a non-sqlite driver
- **THEN** startup fails with a clear configuration error

### Requirement: Project Documentation
The project SHALL include a root README with setup instructions that do not require Docker, PostgreSQL, or Supabase for database setup.

#### Scenario: New developer setup
- **WHEN** a developer follows README setup steps
- **THEN** they can start backend and frontend with only Python venv and SQLite
- **AND** do not need to install or run PostgreSQL
