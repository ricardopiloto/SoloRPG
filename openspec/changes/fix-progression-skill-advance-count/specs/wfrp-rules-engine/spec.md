# Spec delta: wfrp-rules-engine

**Change:** `fix-progression-skill-advance-count`

---

## MODIFIED Requirements

### Requirement: Career Progression Rules

The system SHALL implement WFRP4e career advances: skill advances, talent purchases, and career tier progression within WFRP4e rules. Progression between sessions SHALL occur without LLM involvement. **Each skill advance purchase MUST increment and persist the skill's `advances` count in the character JSON; multiple purchases of the same skill MUST accumulate.**

#### Scenario: Player buys skill advance between sessions

- **WHEN** the player spends XP on a valid skill advance during the progression screen
- **THEN** the system deducts XP per WFRP4e cost tables
- **AND** updates the character's skill advances
- **AND** persists the change before the next session

#### Scenario: Multiple purchases of the same skill accumulate

- **GIVEN** a character with 20+ XP available and Percepção at `advances: 0` (or absent from skills)
- **WHEN** the player buys Percepção +1 four times via the progression API
- **THEN** `xp_spent` increases by 20 (4 × 5 XP)
- **AND** the persisted `skills` entry for Percepção has `advances: 4`
- **AND** `GET /characters/{id}/progression` returns `current_advances: 4` for Percepção

#### Scenario: Progression options reflect persisted advances

- **GIVEN** a character whose Percepção has `advances: 3` in the database
- **WHEN** the progression options endpoint is called
- **THEN** the Percepção row shows `current_advances: 3`
- **AND** the value matches what the sidebar and test resolver use for target calculation
