## MODIFIED Requirements

### Requirement: Quick Roll Skill Resolution
The rules engine SHALL accept quick-roll requests for any skill in the canonical skill catalog, computing target as linked attribute plus owned advances (zero if not owned) plus modifier.

#### Scenario: Owned skill with advances
- **WHEN** the client sends a quick-roll for skill "Atletismo" owned with 2 advances and linked attribute Ag 35
- **THEN** the computed target is 37 before modifier

#### Scenario: Unowned catalog skill
- **WHEN** the client sends a quick-roll for skill "Escalar" not present on the character sheet
- **AND** "Escalar" exists in the skill catalog linked to Strength
- **THEN** the computed target equals the character's Strength value with zero advances
- **AND** no error is raised for missing skill ownership

#### Scenario: Unknown skill rejected
- **WHEN** the client sends a quick-roll for a skill name not in the canonical catalog
- **THEN** the server returns a validation error

## ADDED Requirements

### Requirement: Skill Catalog API
The backend SHALL expose a read-only endpoint returning the canonical WFRP skill catalog with name and linked attribute for each entry.

#### Scenario: List all catalog skills
- **WHEN** the client requests `GET /rules/skills`
- **THEN** the response includes all skills in the canonical catalog sorted alphabetically by name
- **AND** each entry includes `name` and `linked_attribute`
