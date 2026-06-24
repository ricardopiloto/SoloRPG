## MODIFIED Requirements

### Requirement: Phase 1 fixed admin authentication
When `AUTH_MODE` is `fixed_admin`, the system SHALL authenticate users exclusively via a fixed username `admin` and a password defined in the server environment variable `ADMIN_PASSWORD`. The system SHALL NOT expose user registration or email verification in this mode.

#### Scenario: Admin login with env password
- **WHEN** the client submits username `admin` and the correct `ADMIN_PASSWORD`
- **THEN** the API returns a JWT and user profile
- **AND** the admin account is marked as email-verified

#### Scenario: Wrong password rejected
- **WHEN** the client submits username `admin` with an incorrect password
- **THEN** the API returns 401 Unauthorized

#### Scenario: Registration unavailable in phase 1
- **WHEN** `AUTH_MODE` is `fixed_admin` and a client calls `POST /auth/register`
- **THEN** the API returns 404 Not Found

#### Scenario: Admin provisioned on startup
- **WHEN** the backend starts with `AUTH_MODE=fixed_admin` and a valid `ADMIN_PASSWORD`
- **THEN** the system ensures user `admin@wfrp-solo.local` exists with verified email
- **AND** ensures a starter character exists if the admin has none

### Requirement: Email and password registration
The system SHALL allow registration only when `AUTH_MODE` is `multi_user`. In `fixed_admin` mode, registration requirements are deferred to phase 2.

#### Scenario: Registration enabled in multi_user mode
- **WHEN** `AUTH_MODE` is `multi_user`
- **THEN** the existing registration and verification flow applies as specified in add-user-auth

### Requirement: Email and password login
When `AUTH_MODE` is `fixed_admin`, login SHALL accept the fixed admin username and `ADMIN_PASSWORD`. When `AUTH_MODE` is `multi_user`, verified users SHALL log in with email and password as before.

#### Scenario: Fixed admin login in phase 1
- **WHEN** `AUTH_MODE` is `fixed_admin` and credentials match admin + ADMIN_PASSWORD
- **THEN** the API returns a JWT without requiring prior registration

### Requirement: Authenticated session via JWT
Protected API endpoints SHALL require a valid JWT in the Authorization header. This requirement applies in both `fixed_admin` and `multi_user` modes.

#### Scenario: Protected endpoint with valid token
- **WHEN** the client sends a valid Bearer token after admin login
- **THEN** the backend resolves the current user and processes the request

### Requirement: Email delivery adapter
Email verification SHALL be required only when `AUTH_MODE` is `multi_user` and the deployment is production. In `fixed_admin` mode, SMTP is not required.

#### Scenario: No SMTP required in fixed_admin production
- **WHEN** the application starts with `AUTH_MODE=fixed_admin` and `APP_ENV=production`
- **THEN** startup succeeds without SMTP configuration
- **AND** fails if `ADMIN_PASSWORD` is missing or shorter than 8 characters
