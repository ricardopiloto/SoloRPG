## ADDED Requirements

### Requirement: Quick Roll Server Validation
The rules engine SHALL accept quick-roll requests specifying roll type (attribute, skill, or weapon), character stat key, and optional modifier, computing the target number and success levels deterministically on the server.

#### Scenario: Skill quick roll with modifier
- **WHEN** the client sends a quick-roll for skill "Athletics" with modifier +10
- **THEN** the server computes target from character sheet
- **AND** returns roll result, target, and WFRP4e success level
- **AND** the result is persisted in session roll history

#### Scenario: Invalid quick roll rejected
- **WHEN** the client requests a roll for a stat the character does not possess
- **THEN** the server returns HTTP 400 with a descriptive error
- **AND** no roll is recorded
