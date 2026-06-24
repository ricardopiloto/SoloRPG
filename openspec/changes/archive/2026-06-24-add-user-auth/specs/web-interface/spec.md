## ADDED Requirements

### Requirement: Authentication screens
The web interface SHALL provide dedicated screens for registration, email verification, and login. All user-facing copy SHALL be in PT-BR.

#### Scenario: Registration screen
- **WHEN** an unauthenticated visitor opens the registration screen
- **THEN** the UI presents fields for email, password, and password confirmation
- **AND** validates matching passwords before submit

#### Scenario: Verification screen after registration
- **WHEN** registration succeeds
- **THEN** the user is directed to enter the 8-digit email verification code
- **AND** can request code resend with visible rate-limit feedback

#### Scenario: Login screen
- **WHEN** an unauthenticated visitor opens the login screen
- **THEN** the UI presents email and password fields
- **AND** links to registration for new users

### Requirement: Protected application routes
Pages that access user-specific game data SHALL require authentication. Unauthenticated visitors SHALL be redirected to the login screen.

#### Scenario: Redirect when not logged in
- **WHEN** an unauthenticated user navigates to home, character management, or campaigns
- **THEN** the frontend redirects to login
- **AND** preserves intended destination for post-login redirect when practical

#### Scenario: Authenticated access to game data
- **WHEN** a logged-in user navigates to home or character management
- **THEN** the UI loads data scoped to their account

### Requirement: Logout
The interface SHALL allow the authenticated user to log out, clearing the local session token and returning to the login screen.

#### Scenario: User logs out
- **WHEN** the user clicks logout
- **THEN** the stored auth token is cleared
- **AND** subsequent API calls do not send Authorization
- **AND** protected routes redirect to login

## MODIFIED Requirements

### Requirement: Campaign and Character Management Screens
The UI SHALL provide screens for creating and selecting characters and campaigns. These screens SHALL require authentication and SHALL display only resources belonging to the logged-in user.

#### Scenario: Character management access
- **WHEN** the authenticated player is not in an active session
- **THEN** they can access character and campaign management
- **AND** see only their own characters and related campaigns

#### Scenario: Unauthenticated management blocked
- **WHEN** an unauthenticated visitor tries to open character or campaign management
- **THEN** they are redirected to login
