## MODIFIED Requirements

### Requirement: Custom Character Creation
The player SHALL be able to create a custom character by defining attributes, initial career, and background before starting a campaign. **In phase 1 (auth MVP rollout), custom creation via the multi-step wizard SHALL NOT be exposed**; players SHALL obtain playable characters only through pre-generated templates or the automatic starter character created on account verification. When custom creation is re-enabled via configuration, the wizard SHALL require authentication and persist characters with ownership linked to the authenticated user.

#### Scenario: Custom creation deferred in phase 1
- **WHEN** custom character creation is disabled by configuration
- **THEN** the public API rejects wizard creation requests with 403 Forbidden
- **AND** the player can still create characters via pre-generated templates
- **AND** new accounts still receive a valid starter character on email verification

#### Scenario: Custom character creation flow (when enabled)
- **WHEN** custom creation is enabled and the authenticated player chooses custom creation
- **THEN** the system presents WFRP4e-valid attribute, career, and background options
- **AND** validates the character against WFRP4e creation rules
- **AND** persists the character linked to the user's account before campaign start

#### Scenario: Unauthenticated character creation blocked
- **WHEN** a client without a valid token attempts to create a character
- **THEN** the API returns 401 Unauthorized

### Requirement: Pre-Generated Character Selection
The player SHALL be able to select a pre-generated character for quick entry into a campaign. Pre-generated character instantiation SHALL remain available in phase 1. When authentication is enforced, pregen instantiation SHALL require authentication and SHALL associate the new character with the current user.

#### Scenario: Pre-generated character selection
- **WHEN** the authenticated player chooses a pre-generated character
- **THEN** the system loads a valid WFRP4e character template
- **AND** allows the player to confirm or customize the name
- **AND** persists the character linked to the user's account for campaign use

#### Scenario: Pregens available while wizard hidden
- **WHEN** custom creation is disabled in phase 1
- **THEN** pre-generated selection endpoints and UI remain available
- **AND** the player can start a campaign with a selected pregen character
