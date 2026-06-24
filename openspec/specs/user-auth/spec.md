# user-auth Specification

## Purpose
TBD - created by archiving change add-user-auth. Update Purpose after archive.
## Requirements
### Requirement: Email and password registration
The system SHALL allow a new user to register with a valid email address, a password, and password confirmation. The email SHALL be validated for RFC-compliant format and stored normalized (lowercase, trimmed). Passwords SHALL match and meet a minimum length of 8 characters.

#### Scenario: Successful registration
- **WHEN** the user submits a valid email, matching password and confirmation
- **THEN** the system creates an unverified user account
- **AND** sends an 8-digit verification code to the registered email
- **AND** returns a response indicating verification is required before login

#### Scenario: Invalid email rejected
- **WHEN** the user submits a malformed email address
- **THEN** the API returns a validation error
- **AND** no user account is created

#### Scenario: Password mismatch rejected
- **WHEN** password and confirmation do not match
- **THEN** the API returns a validation error
- **AND** no user account is created

#### Scenario: Duplicate email rejected
- **WHEN** the email is already registered
- **THEN** the API returns an error without revealing whether the account is verified

### Requirement: One-time email verification with 8-digit code
On first registration only, the system SHALL require the user to enter the unique 8-digit numeric code sent to their email before the account is authorized to log in. Verification codes SHALL expire after 15 minutes and SHALL be invalidated after 5 failed attempts.

#### Scenario: Successful verification
- **WHEN** the user submits the correct non-expired code for their unverified account
- **THEN** the system marks the email as verified
- **AND** issues an authentication token
- **AND** creates a random WFRP4e starter character for the account

#### Scenario: Wrong code increments attempts
- **WHEN** the user submits an incorrect code
- **THEN** the attempt counter increments
- **AND** the account remains unverified

#### Scenario: Expired code rejected
- **WHEN** the user submits a code past its expiration time
- **THEN** the API returns an error
- **AND** the user must request a new code

#### Scenario: Resend verification code
- **WHEN** the user requests a new verification code for an unverified account
- **THEN** the system sends a new 8-digit code
- **AND** rate-limits resend to at most once per minute per email

### Requirement: Email and password login
Verified users SHALL log in with email and password and receive a JWT bearer token. Unverified users SHALL NOT receive a token.

#### Scenario: Successful login
- **WHEN** a verified user submits correct email and password
- **THEN** the API returns a JWT and user profile

#### Scenario: Unverified user blocked from login
- **WHEN** an unverified user submits correct credentials
- **THEN** the API returns forbidden with verification_required
- **AND** does not issue a token

#### Scenario: Invalid credentials rejected
- **WHEN** email or password is incorrect
- **THEN** the API returns unauthorized

### Requirement: Authenticated session via JWT
Protected API endpoints SHALL require a valid JWT in the Authorization header. Invalid or missing tokens SHALL return 401 Unauthorized.

#### Scenario: Protected endpoint with valid token
- **WHEN** the client sends a valid Bearer token
- **THEN** the backend resolves the current user and processes the request

#### Scenario: Protected endpoint without token
- **WHEN** the client calls a protected endpoint without Authorization
- **THEN** the API returns 401 Unauthorized

### Requirement: Email delivery adapter
The backend SHALL send verification emails through a pluggable email adapter. Development and tests SHALL use a mock adapter that does not require external SMTP.

#### Scenario: Mock email in tests
- **WHEN** EMAIL_PROVIDER is mock
- **THEN** verification codes are captured without external network calls
- **AND** tests can complete the verify flow deterministically

#### Scenario: SMTP email in production
- **WHEN** EMAIL_PROVIDER is smtp with valid configuration
- **THEN** the adapter sends the 8-digit code to the user's email address

