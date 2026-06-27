# Spec delta: gm-narrative

**Change:** `strengthen-gm-test-triggers`

---

## ADDED Requirements

### Requirement: Contested outcome tests MUST NOT be replaced by passive discovery tests

When a scene requires resolving a **contested outcome** (chase, stealth infiltration, combat exchange), the GM SHALL emit a mandatory situational or combat `[TESTE]` as defined in the GM system prompt. Passive discovery tests (`obrigatorio: false`, TIPO 3) SHALL NOT substitute for Atletismo, Furtividade, or combat attack/defense rolls.

#### Scenario: Chase is not passive Perception

- **GIVEN** an NPC is fleeing and the player pursues
- **WHEN** the GM must resolve whether the player catches up
- **THEN** the GM emits `[TESTE]` with skill `Atletismo`
- **AND** does NOT use a passive Percepção test instead
- **AND** does NOT narrate the outcome without a roll

#### Scenario: Stealth entry is not ambient discovery

- **GIVEN** the player declares a stealthy approach
- **WHEN** detection vs. success is the contested outcome
- **THEN** the GM emits `[TESTE]` with skill `Furtividade`
- **AND** does NOT treat it as TIPO 3 passive discovery with `obrigatorio: false` only

#### Scenario: Passive discovery still applies to sensory depth

- **GIVEN** the GM narrated a partial sensory stimulus (footsteps, a vague shadow)
- **WHEN** a deeper detail could be revealed without changing the contested outcome
- **THEN** the GM MAY still emit TIPO 3 passive `[TESTE]` (Percepção, `obrigatorio: false`)
- **AND** this is separate from any mandatory Atletismo/Furtividade/combat test in the same turn (max one passive per turn rule unchanged)
