## ADDED Requirements

### Requirement: Environment-based auth mode
The system SHALL distinguish development and production via `APP_ENV`. Production SHALL require full email verification for new accounts. Development SHALL provision a master development account for normal login without special bypass endpoints.

#### Scenario: Production requires verification
- **WHEN** `APP_ENV` is `production`
- **THEN** new registrations require email verification before login
- **AND** no master development user is provisioned

#### Scenario: Development provisions master user
- **WHEN** the backend starts with `APP_ENV=development`
- **THEN** a verified user with email `dev@localhost` exists or is created
- **AND** the user has at least one starter character if none existed

### Requirement: Master development login via standard endpoint
In development only, the system SHALL allow authentication of the master user through `POST /auth/login` using password `dev` and email `dev@localhost` or alias `dev`.

#### Scenario: Login with dev alias
- **WHEN** the client submits email `dev` and password `dev` with `APP_ENV=development`
- **THEN** the API returns a JWT and user profile
- **AND** no separate dev-login endpoint is required

#### Scenario: Login with canonical dev email
- **WHEN** the client submits email `dev@localhost` and password `dev` with `APP_ENV=development`
- **THEN** the API returns a JWT and user profile

#### Scenario: Master credentials rejected in production
- **WHEN** the client submits email `dev` and password `dev` with `APP_ENV=production`
- **THEN** the API returns unauthorized
- **AND** no master user exists in the database from startup seeding

### Requirement: Production startup safety
When `APP_ENV` is `production`, the application SHALL NOT provision the master development user and SHALL validate critical auth configuration at startup.

#### Scenario: Production blocks default JWT secret
- **WHEN** the application starts with `APP_ENV=production` and placeholder `JWT_SECRET`
- **THEN** startup fails with a clear error

## MODIFIED Requirements

### Requirement: Email and password login
Verified users SHALL log in with email and password and receive a JWT bearer token. Unverified users SHALL NOT receive a token in production. In development, the master user SHALL always be verified and loginable via the standard login endpoint.

#### Scenario: Successful login in production
- **WHEN** a verified user submits correct email and password with `APP_ENV=production`
- **THEN** the API returns a JWT and user profile

#### Scenario: Unverified user blocked in production
- **WHEN** an unverified user submits correct credentials with `APP_ENV=production`
- **THEN** the API returns forbidden with verification_required

#### Scenario: Master dev login in development
- **WHEN** credentials `dev` / `dev` are submitted with `APP_ENV=development`
- **THEN** the API returns a JWT via the standard login flow

#### Scenario: Invalid credentials rejected
- **WHEN** email or password is incorrect
- **THEN** the API returns unauthorized regardless of environment

### Requirement: Email delivery adapter
The backend SHALL send verification emails through a pluggable email adapter. Development MAY use mock delivery without SMTP. Production SHALL use SMTP for verification emails.

#### Scenario: Mock email in development
- **WHEN** `APP_ENV` is development or `EMAIL_PROVIDER` is mock
- **THEN** verification codes are not sent via external SMTP
- **AND** the master user can authenticate without email verification flow

#### Scenario: SMTP email in production
- **WHEN** `APP_ENV` is production and `EMAIL_PROVIDER` is smtp with valid configuration
- **THEN** the adapter sends the 8-digit code to the user's email address
