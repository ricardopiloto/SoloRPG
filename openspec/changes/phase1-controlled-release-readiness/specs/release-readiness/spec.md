## ADDED Requirements

### Requirement: Phase 1 controlled release scope
The project SHALL define Phase 1 controlled release as: authenticated multi-user access with email verification in production, automatic starter character on signup, pre-generated character selection only (custom wizard disabled), and the existing WFRP solo game loop (campaign → session → rolls → recap → progression) behind authentication.

#### Scenario: External tester onboarding
- **WHEN** a new user registers on the production deployment
- **THEN** they receive an email verification code
- **AND** after verification receive a playable starter character
- **AND** can start a campaign without using custom character creation

#### Scenario: Custom creation unavailable in phase 1
- **WHEN** custom character creation is disabled by configuration
- **THEN** the character page shows only pre-generated templates
- **AND** wizard API endpoints return 403 Forbidden

### Requirement: Environment segregation for release
The system SHALL distinguish development and production via `APP_ENV`. Development SHALL allow mocked or bypassed email verification. Production SHALL require real email verification and SHALL NOT expose development auth bypass endpoints.

#### Scenario: Production requires verification
- **WHEN** `APP_ENV` is `production`
- **THEN** registration does not return a JWT until email is verified
- **AND** the master development user is not provisioned at startup

#### Scenario: Development allows fast access
- **WHEN** `APP_ENV` is `development`
- **THEN** the developer can authenticate via `POST /auth/login` with master credentials `dev` / `dev`
- **AND** protected game routes remain scoped to the authenticated user

### Requirement: Production configuration guards
The backend SHALL fail fast on startup in production when critical secrets or email delivery are misconfigured.

#### Scenario: Default JWT secret rejected in production
- **WHEN** the application starts with `APP_ENV=production` and default or placeholder `JWT_SECRET`
- **THEN** startup fails with a clear error message

#### Scenario: SMTP required in production
- **WHEN** the application starts with `APP_ENV=production` and `EMAIL_PROVIDER` is not `smtp`
- **THEN** startup fails with a clear error message

### Requirement: Release validation gates
Before inviting external testers, the project SHALL complete documented manual validation of authentication isolation and at least one full game loop session behind login.

#### Scenario: Auth isolation sign-off
- **WHEN** release validation is performed
- **THEN** two separate accounts cannot access each other's characters
- **AND** unauthenticated clients receive 401 on protected game APIs

#### Scenario: E2E covers authenticated game loop
- **WHEN** the E2E test suite runs
- **THEN** it authenticates before character selection
- **AND** completes pregen → campaign → session → roll → recap without error

### Requirement: Phase 1 deploy runbook
The project SHALL document environment variables and deployment steps required for a controlled production or staging test, including JWT, SMTP, CORS, database, and feature flags.

#### Scenario: Operator deploys staging
- **WHEN** an operator follows the phase 1 release runbook
- **THEN** they can configure backend and frontend with production auth settings
- **AND** verify health endpoint and a test registration flow
