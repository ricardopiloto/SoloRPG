## MODIFIED Requirements

### Requirement: Phase 1 controlled release scope
Phase 1 controlled release SHALL use `AUTH_MODE=fixed_admin` with a single shared admin account and password from `ADMIN_PASSWORD`. Multi-user registration and email verification are deferred to phase 2.

#### Scenario: Controlled test without account creation
- **WHEN** testers access the deployed phase 1 application
- **THEN** they authenticate with the shared admin password provided by the operator
- **AND** cannot self-register new accounts

#### Scenario: Environment segregation for release
When `AUTH_MODE` is `fixed_admin`, production startup SHALL require `ADMIN_PASSWORD` and a secure `JWT_SECRET` but SHALL NOT require SMTP.

#### Scenario: External tester onboarding (phase 1)
- **WHEN** a tester receives the shared access password from the operator
- **THEN** they can log in and play using pre-generated characters and the admin starter
- **AND** share the same game data as other testers on the same deployment
