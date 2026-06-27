# Spec delta: synthetic-gm

**Change:** `add-gm-social-test-triggers`

---

## ADDED Requirements

### Requirement: GM MUST emit tests for mandatory social interaction triggers

When the player attempts to influence an NPC or explicitly asks to read veracity or hidden intent, the GM SHALL emit a `[TESTE]` signal and pause resolution until the backend returns the roll result. The GM SHALL NOT narrate the social outcome (new information revealed, lie confirmed or denied) before the test completes.

#### Scenario: Player tries to extract information from an NPC

- **GIVEN** the player declares intent to get more information from an NPC (e.g. "quero tentar extrair mais informações da dona da taverna")
- **WHEN** success or failure of obtaining the information matters and is uncertain
- **THEN** the GM emits `[TESTE]` with skill `Charme` (Fellowship)
- **AND** waits for `[RESULTADO DO SISTEMA]` before revealing secrets or refusal
- **AND** does NOT narrate the NPC confiding freely without a roll

#### Scenario: Player asks whether an NPC is lying

- **GIVEN** the player explicitly asks to detect deception (e.g. "percebo se ele está mentindo?")
- **WHEN** the answer depends on the character's social insight
- **THEN** the GM emits `[TESTE]` with skill `Intuição` (Initiative)
- **AND** waits for the result before narrating certainty of deception or continued ambiguity
- **AND** does NOT narrate "you clearly see he is lying" without a roll

#### Scenario: Casual conversation without stakes

- **GIVEN** the player asks a trivial question with no meaningful failure consequence (e.g. directions to the market)
- **WHEN** no influence or deception reading is being attempted
- **THEN** the GM MAY narrate without `[TESTE]`
- **AND** mandatory social triggers do NOT apply
