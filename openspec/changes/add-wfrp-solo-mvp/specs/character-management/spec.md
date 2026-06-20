## ADDED Requirements

### Requirement: WFRP4e Character Sheet
The system SHALL maintain a character sheet faithful to WFRP4e including: attributes (WS, BS, S, T, I, Ag, Dex, Int, WP, Fel), wounds (current/max), Fate Points (current/max), Fortune Points, careers (name, tier, advances spent), skills (name, advances, linked attribute), talents, and trappings (name, encumbrance, description).

#### Scenario: Character sheet display
- **WHEN** the player views their character during or between sessions
- **THEN** the UI displays all WFRP4e sheet fields
- **AND** Fate Points are visible as a finite precious resource

### Requirement: Custom Character Creation
The player SHALL be able to create a custom character by defining attributes, initial career, and background before starting a campaign.

#### Scenario: Custom character creation flow
- **WHEN** the player chooses custom creation
- **THEN** the system presents WFRP4e-valid attribute, career, and background options
- **AND** validates the character against WFRP4e creation rules
- **AND** persists the character before campaign start

### Requirement: Pre-Generated Character Selection
The player SHALL be able to select a pre-generated character for quick entry into a campaign.

#### Scenario: Pre-generated character selection
- **WHEN** the player chooses a pre-generated character
- **THEN** the system loads a valid WFRP4e character template
- **AND** allows the player to confirm or customize the name
- **AND** persists the character for campaign use

### Requirement: Between-Session Progression
The player SHALL spend earned XP between sessions to purchase skill advances, talents, and career advances via a dedicated interface without LLM involvement.

#### Scenario: Progression after session with XP
- **WHEN** a session ends and the character has unspent XP
- **THEN** the system presents available advances per WFRP4e rules
- **AND** applies purchases immediately upon confirmation
- **AND** blocks progression during an active non-pausable session

### Requirement: Permanent Character Death
When a character dies (Fate Points exhausted on lethal critical), the character SHALL be marked permanently dead. The character's Fate Points SHALL NOT reset between campaigns in the MVP.

#### Scenario: Character death
- **WHEN** the character dies during a session
- **THEN** the system marks the character status as dead
- **AND** preserves the character record and campaign history
- **AND** does NOT restore Fate Points if the player starts a new campaign with a different character

#### Scenario: Continue same character in new campaign
- **WHEN** the player starts a new campaign continuing an existing living character
- **THEN** the character retains current Fate Points, XP, skills, and inventory state
- **AND** does NOT receive a Fate Point refresh

### Requirement: Character Persistence Across Sessions
The system SHALL persist all character state changes (wounds, inventory, XP, skills, talents, karma, reputation) to the database after each mechanical resolution and session end.

#### Scenario: Session ends with inventory change
- **WHEN** a session ends and the character gained or lost items
- **THEN** the system persists updated trappings/inventory
- **AND** the inventory is available at the start of the next session
