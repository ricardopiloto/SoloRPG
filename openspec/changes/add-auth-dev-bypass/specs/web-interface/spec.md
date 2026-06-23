## ADDED Requirements

### Requirement: Development login hint
When `NEXT_PUBLIC_APP_ENV` is `development`, the login screen SHALL display a hint that the master development credentials are `dev` / `dev` (email alias `dev` or `dev@localhost`).

#### Scenario: Dev hint visible locally
- **WHEN** the user opens `/login` with `NEXT_PUBLIC_APP_ENV=development`
- **THEN** a hint about dev/dev credentials is shown
- **AND** the user can submit the standard login form without visiting register or verify-email

#### Scenario: Dev hint hidden in production build
- **WHEN** `NEXT_PUBLIC_APP_ENV` is `production`
- **THEN** the development credentials hint is not rendered

### Requirement: Dev credential prefill
When `NEXT_PUBLIC_APP_ENV` is `development`, the login form SHALL pre-fill email `dev` and password `dev` to reduce friction.

#### Scenario: Prefill in development
- **WHEN** the login page loads in development mode
- **THEN** email and password fields default to `dev` and `dev`
- **AND** the user can still edit fields before submit

## MODIFIED Requirements

### Requirement: Registration redirect respects environment
After registration, the frontend SHALL redirect to email verification when the API indicates verification is required. Development master login does not use the registration flow.

#### Scenario: Production register redirects to verify
- **WHEN** registration succeeds without access_token
- **THEN** the user is directed to `/verify-email`

#### Scenario: Development daily workflow uses login only
- **WHEN** a developer starts local work
- **THEN** they authenticate via `/login` with dev/dev without completing registration
