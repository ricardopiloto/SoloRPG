# Spec delta: wfrp-rules-engine

**Change:** `add-gm-social-test-triggers`

---

## ADDED Requirements

### Requirement: Skill catalog MUST include Intuição linked to Initiative

The MVP skill catalog SHALL include `Intuição` with linked attribute `I` (Initiative), consistent with WFRP4e. The skill SHALL be available via the skills API, quick-roll validation, and progression skill lists.

#### Scenario: Skills API lists Intuição

- **WHEN** the client requests the skill catalog
- **THEN** the response includes an entry `{ "name": "Intuição", "linked_attribute": "I" }`

#### Scenario: GM test resolves Intuição with Initiative

- **WHEN** the backend receives a `[TESTE]` with `"pericia": "Intuição"`
- **THEN** the system resolves the test using attribute `I` plus the character's Intuição advances (if any)
- **AND** returns success/failure levels to the LLM for narration

#### Scenario: Quick-roll accepts Intuição

- **WHEN** the player performs a sidebar quick-roll for skill `Intuição`
- **THEN** the system validates the skill against the catalog without error
- **AND** rolls using `I` plus owned advances
