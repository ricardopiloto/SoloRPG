## MODIFIED Requirements

### Requirement: Random starter character on signup
When `AUTH_MODE` is `fixed_admin`, the system SHALL provision a random WFRP4e starter character for the admin user on startup if none exists. When `AUTH_MODE` is `multi_user`, starter creation on first email verification remains as specified.

#### Scenario: Starter for admin on startup
- **WHEN** the backend starts in `fixed_admin` mode and the admin user has no characters
- **THEN** the system generates and persists a random valid starter character for the admin account

#### Scenario: Starter not duplicated
- **WHEN** the admin user already has a starter character
- **THEN** startup does not create another starter
