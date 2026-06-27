# Spec delta: wfrp-rules-engine

**Change:** `fix-wfrp-success-levels`

---

## MODIFIED Requirements

### Requirement: Attribute and Skill Tests

The system SHALL resolve WFRP4e d100 tests with success/failure levels based on roll vs. target (attribute + skill advances + modifiers). On success, levels SHALL equal `1 + (target - roll) // 10` (WFRP4e margin in tens, including the base success level). On failure, levels SHALL equal `1 + (roll - target) // 10`.

#### Scenario: Successful skill test with margin

- **WHEN** a test roll is below or equal to the target value
- **THEN** the system calculates success levels using the WFRP4e tens-margin formula
- **AND** returns the level to the LLM for narrative consequence

#### Scenario: Target 32 roll 3 yields three success levels

- **WHEN** the computed target is 32 and the d100 roll is 3
- **THEN** the test succeeds
- **AND** `levels` equals **3** (not 2)

#### Scenario: Marginal success one level

- **WHEN** the computed target is 40 and the d100 roll is 34
- **THEN** the test succeeds
- **AND** `levels` equals **1**

#### Scenario: Failed skill test

- **WHEN** a test roll exceeds the target value
- **THEN** the system calculates failure level using `1 + (roll - target) // 10`
- **AND** returns failure details for LLM narration of consequencia_falha

#### Scenario: Roll results include levels field

- **WHEN** the backend returns `roll_results` for a test or quick-roll
- **THEN** each result includes numeric `levels` for client display
- **AND** the client MUST NOT recalculate levels with a different formula
