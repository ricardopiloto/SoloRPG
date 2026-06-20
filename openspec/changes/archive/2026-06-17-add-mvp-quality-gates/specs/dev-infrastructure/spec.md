## ADDED Requirements

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
