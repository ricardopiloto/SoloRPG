## ADDED Requirements

### Requirement: Database Profile Selection
The system SHALL support configurable database profiles via `DATABASE_PROFILE`: `sqlite-dev` (zero-dependency local), `postgres` (local or containerized PostgreSQL + pgvector), and `supabase` (remote PostgreSQL + pgvector).

#### Scenario: Developer starts with SQLite profile
- **WHEN** `DATABASE_PROFILE=sqlite-dev` is set and no `DATABASE_URL` override exists
- **THEN** the backend uses SQLite with async driver
- **AND** starts without Docker or external database services

#### Scenario: Developer uses PostgreSQL profile
- **WHEN** `DATABASE_PROFILE=postgres` and `DATABASE_URL` points to a running PostgreSQL instance
- **THEN** the backend connects to PostgreSQL
- **AND** enables pgvector extension on startup

#### Scenario: Developer uses Supabase profile
- **WHEN** `DATABASE_PROFILE=supabase` and `DATABASE_URL` contains a Supabase connection string
- **THEN** the backend connects to remote PostgreSQL
- **AND** enables pgvector if available on the remote instance

### Requirement: Conditional pgvector Initialization
The system SHALL execute `CREATE EXTENSION IF NOT EXISTS vector` only when connected to PostgreSQL. SQLite and other non-PostgreSQL backends SHALL NOT attempt pgvector initialization.

#### Scenario: SQLite dev startup
- **WHEN** the backend starts with `sqlite-dev` profile
- **THEN** no pgvector extension command is executed
- **AND** database tables are created successfully

### Requirement: Development Health Diagnostics
The system SHALL expose database profile and connection status via `GET /health` for local troubleshooting.

#### Scenario: Health check after successful SQLite startup
- **WHEN** a client calls `GET /health`
- **THEN** the response includes `database_profile` and `database_ok: true`

### Requirement: Local Setup Documentation
The project SHALL document at least four local database setup paths: SQLite-dev (no install), Docker Compose, Podman Compose, and Supabase cloud.

#### Scenario: Fedora user without Docker daemon
- **WHEN** the developer reads the README troubleshooting section
- **THEN** they find instructions for Podman, native PostgreSQL, SQLite-dev, or starting the Docker service
- **AND** can choose a path without being blocked by `docker.sock` errors

### Requirement: Development Prerequisites Check Script
The project SHALL provide a script that verifies Python venv, Node/npm, database reachability, and optional LLM API key configuration.

#### Scenario: Run check script before first session
- **WHEN** the developer runs `scripts/check-dev.sh`
- **THEN** the script reports pass/fail for each prerequisite
- **AND** suggests the appropriate `DATABASE_PROFILE` if database is unreachable

### Requirement: Actionable Database Startup Errors
When PostgreSQL connection fails during application startup, the system SHALL emit a log message identifying the configured host/port, likely causes, and remediation options (start container, use `sqlite-dev`, or configure Supabase).

#### Scenario: PostgreSQL unreachable on port 5432
- **WHEN** `DATABASE_PROFILE=postgres` and no PostgreSQL server accepts connections at the configured URL
- **THEN** startup fails with a message mentioning port/host and suggesting `DATABASE_PROFILE=sqlite-dev` as immediate workaround
- **AND** does not fail with only a raw `ConnectionResetError` stack trace

#### Scenario: SQLite dev starts without external database
- **WHEN** `DATABASE_PROFILE=sqlite-dev` is configured
- **THEN** uvicorn completes application startup without connecting to port 5432
- **AND** `GET /health` returns `database_ok: true`

### Requirement: Default Dev Profile for New Clones
The project `.env.example` SHALL default to `DATABASE_PROFILE=sqlite-dev` so new developers can run the backend without Docker or PostgreSQL installed.

#### Scenario: Fresh clone first run
- **WHEN** a developer copies `.env.example` to `backend/.env` without editing database settings
- **THEN** the backend starts successfully using SQLite
- **AND** README explains how to upgrade to PostgreSQL when ready
