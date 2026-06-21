## MODIFIED Requirements

### Requirement: Fate Points on Character Sheet Panel
The character sheet side panel SHALL display Fate Points (current/max) and Fortune Points (current/max) as separate visible finite resources using gem indicators.

#### Scenario: Fate and Fortune display
- **WHEN** the player views the character sidebar during a session
- **THEN** Fate Points are shown as current/max gem indicators (◆ filled, ◇ empty)
- **AND** Fortune Points are shown as a separate current/max gem row below or beside Fate
- **AND** both update immediately after expenditure during the session

#### Scenario: Fortune spend prompt on failed test
- **WHEN** a GM-requested test fails and the character has Fortune Points remaining
- **THEN** the UI SHALL offer an option to spend a Fortune Point to re-roll
- **AND** SHALL NOT offer a +10 bonus alternative
