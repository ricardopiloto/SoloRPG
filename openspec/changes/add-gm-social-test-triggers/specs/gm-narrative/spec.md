# Spec delta: gm-narrative

**Change:** `add-gm-social-test-triggers`

---

## ADDED Requirements

### Requirement: Player-initiated social reading MUST use contested Intuição test

When the player explicitly requests to detect lies or read hidden intent, the GM SHALL emit a contested `[TESTE]` (TIPO 1) with skill `Intuição` and explicit success/failure consequences. Passive discovery tests (TIPO 3, `obrigatorio: false`) SHALL NOT substitute for this resolution.

#### Scenario: Explicit lie check is not passive discovery

- **GIVEN** the player asks "percebo se ele está mentindo?"
- **WHEN** the GM must resolve whether the character detects deception
- **THEN** the GM emits `[TESTE]` with `pericia: "Intuição"` and contested consequences
- **AND** does NOT use TIPO 3 passive format as the sole resolution
- **AND** does NOT narrate the outcome without a roll

#### Scenario: Passive Intuição still applies for ambient social cues

- **GIVEN** the GM narrated evasive speech without the player asking for a lie check
- **WHEN** a deeper layer could be revealed without resolving "is he lying?" as the primary outcome
- **THEN** the GM MAY emit TIPO 3 passive `[TESTE]` with `obrigatorio: false`
- **AND** this is separate from player-initiated contested Intuição in the same turn (one passive per turn rule unchanged)

#### Scenario: Charme is not Percepção

- **GIVEN** the player tries to persuade or extract information socially
- **WHEN** the outcome depends on social skill rather than sensory observation
- **THEN** the GM emits `[TESTE]` with `pericia: "Charme"`
- **AND** does NOT use Percepção or passive discovery instead
