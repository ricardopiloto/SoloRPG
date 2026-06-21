## ADDED Requirements

### Requirement: Fortune refresh on session start
When a new game session is created, the system SHALL initialize Fortune Points from the character's current Fate Points before the first turn.

#### Scenario: New session initializes Fortune from Fate
- **WHEN** `start_session()` creates a new `GameSession` (not returning a paused session)
- **THEN** the character's `fortune_current` and `fortune_max` are set to `fate_current`
- **AND** the values are persisted before gameplay begins

#### Scenario: Paused session resume skips Fortune refresh
- **WHEN** `start_session()` returns an existing paused active session
- **THEN** Fortune Points are not recalculated from Fate Points
