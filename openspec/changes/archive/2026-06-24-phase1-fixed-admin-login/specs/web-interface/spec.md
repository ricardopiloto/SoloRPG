## MODIFIED Requirements

### Requirement: Authentication screens
The web interface SHALL provide a login screen. When `AUTH_MODE` is `fixed_admin`, the UI SHALL NOT offer registration or email verification screens.

#### Scenario: Password-only login in phase 1
- **WHEN** the application runs in `fixed_admin` mode
- **THEN** the login screen prompts only for the access password
- **AND** uses the fixed username `admin` without user input
- **AND** does not link to registration

#### Scenario: Registration route blocked
- **WHEN** a visitor navigates to `/register` or `/verify-email` in `fixed_admin` mode
- **THEN** the frontend redirects to `/login`

#### Scenario: Multi-user screens in phase 2
- **WHEN** `AUTH_MODE` is `multi_user`
- **THEN** registration and verification screens remain available as specified in add-user-auth

### Requirement: Protected application routes
Pages that access game data SHALL require authentication via JWT in all auth modes.

#### Scenario: Redirect when not logged in
- **WHEN** an unauthenticated user navigates to home, character management, or campaigns
- **THEN** the frontend redirects to login
