## ADDED Requirements

### Requirement: Resume Active Campaign
The UI SHALL allow the player to resume an active campaign and start a new session from the home screen.

#### Scenario: Continue active campaign
- **WHEN** the player selects an active campaign from history
- **THEN** the UI offers "Continuar" to start a new session
- **AND** loads preserved character and campaign context

### Requirement: New Campaign Character Choice
When starting a new campaign after completion or death, the UI SHALL prompt the player to continue with an existing living character or create a new character.

#### Scenario: New campaign after death
- **WHEN** the player's character died in a previous campaign
- **THEN** the UI prompts to create a new character or select another living character
- **AND** does not allow continuing with the dead character

### Requirement: Custom Character Creation UI
The UI SHALL provide a form for custom WFRP4e character creation (attributes, career, background) in addition to pre-generated templates.

#### Scenario: Custom character creation
- **WHEN** the player chooses custom creation
- **THEN** the UI presents valid WFRP4e creation fields
- **AND** submits to the character creation API

## MODIFIED Requirements

### Requirement: Campaign Lifecycle States
Each campaign SHALL have status active, completed, or unfinished. The system SHALL expose an API to mark a campaign as completed when the central narrative objective resolves.

#### Scenario: Campaign completed via API
- **WHEN** the narrative objective is resolved and completion is triggered
- **THEN** the system marks the campaign status as concluída
- **AND** preserves full history

### Requirement: Between-Session Progression
The progression screen SHALL list all valid skill and talent advances available for purchase with current XP, not a single hardcoded option.

#### Scenario: Progression choices displayed
- **WHEN** the player opens progression after a session with unspent XP
- **THEN** the UI lists purchasable advances with XP costs
- **AND** applies purchases via progression API
