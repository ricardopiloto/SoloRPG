# dev-infrastructure Specification

## Purpose
TBD - created by archiving change add-mvp-quality-gates. Update Purpose after archive.
## Requirements
### Requirement: API Integration Test Suite
The project SHALL include automated API integration tests covering character creation, campaign lifecycle, session start, and turn processing.

#### Scenario: API test suite runs in CI
- **WHEN** `pytest tests/` runs in CI or locally with test database
- **THEN** character, campaign, and session endpoints are exercised
- **AND** failures block merge

### Requirement: End-to-End Game Loop Test
The project SHALL include an E2E test covering: create character → start campaign → session turn → progression screen.

#### Scenario: Playwright E2E passes
- **WHEN** E2E test runs against local stack
- **THEN** the main game loop completes without errors

### Requirement: Project Documentation
The project SHALL include a root README with setup instructions for DeepSeek LLM, database profiles, backend, frontend, and common troubleshooting.

#### Scenario: New developer setup
- **WHEN** a developer follows README setup steps
- **THEN** they can start backend and frontend with DeepSeek configured
- **AND** find troubleshooting for Docker and PostgreSQL connection errors

### Requirement: Documentation Stack Alignment
Project documentation in `Docs/` SHALL reflect the implemented technology stack: FastAPI/Python backend, Next.js frontend, DeepSeek as default LLM provider, and Open Design prototype as UI reference.

#### Scenario: Developer reads technical research
- **WHEN** a developer opens `Docs/technical-research.md`
- **THEN** the architecture diagram shows FastAPI backend
- **AND** the LLM section documents the model-agnostic adapter with DeepSeek as implementation default

#### Scenario: Developer finds UI reference
- **WHEN** a developer opens `Docs/README.md`
- **THEN** they find links to ux-spec, prototype gap analysis, and Open Design project path
- **AND** the development order references `add-frontend-prototype-parity` instead of superseded proposals

