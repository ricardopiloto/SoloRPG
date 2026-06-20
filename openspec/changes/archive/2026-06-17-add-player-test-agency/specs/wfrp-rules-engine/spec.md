## MODIFIED Requirements

### Requirement: Server-Side Dice Rolling
The system SHALL roll all dice server-side when the player confirms a pending test. Automatic rolling during the initial GM response turn SHALL NOT occur.

#### Scenario: Roll deferred until player action
- **WHEN** the GM emits `[TESTE]` in a turn response
- **THEN** no dice are rolled in that request
- **AND** dice are rolled only when the player invokes the roll endpoint
