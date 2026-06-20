## ADDED Requirements

### Requirement: Pending Test State
When the GM emits a `[TESTE]` signal, the system SHALL persist the test payload as a pending test on the active session and SHALL NOT roll dice until the player explicitly confirms.

#### Scenario: GM requests skill test
- **WHEN** the GM response contains a `[TESTE]` signal
- **THEN** the backend stores pending test data on the session
- **AND** returns test metadata to the frontend without roll results
- **AND** sets session phase to awaiting player roll confirmation

### Requirement: Player-Initiated Roll
The player SHALL trigger dice resolution by clicking "Rolar dado" in the UI. The backend SHALL roll d100 server-side only upon this action.

#### Scenario: Player clicks roll button
- **WHEN** the player clicks "Rolar dado" on a pending test card
- **THEN** the backend rolls d100 server-side
- **AND** returns roll value, target, success/failure, and SL to the UI
- **AND** triggers GM narration of the consequence with roll result injected

### Requirement: Test Prompt UI Card
The UI SHALL display a highlighted test card in the chat area showing test name, attribute, current value, situational modifier, and a "Rolar dado" button.

#### Scenario: Test card displayed
- **WHEN** a pending test exists on the active session
- **THEN** the chat shows a test card with attribute and modifier details
- **AND** a "Rolar dado" button is visible and enabled
- **AND** GM consequence text is not shown until after the roll

## MODIFIED Requirements

### Requirement: Dice Roll Animation
When the backend resolves a `[TESTE]` roll, the UI SHALL display a dice roll animation and the numeric result BEFORE the GM narrates the consequence. The animation SHALL begin only after the player clicks "Rolar dado".

#### Scenario: Visible dice roll sequence
- **WHEN** the player confirms a pending test roll
- **THEN** the UI animates the d100 roll
- **AND** displays roll value, target, and success/failure level
- **AND** only then requests/displays the GM narrative consequence
