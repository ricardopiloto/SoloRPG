# Spec delta: synthetic-gm

**Change:** `strengthen-gm-test-triggers`

---

## MODIFIED Requirements

### Requirement: Combat Narration Protocol

In COMBATE mode, the GM SHALL announce whose turn it is, wait for player action on player turns, emit required `[TESTE]` signals for **every** mechanical exchange (attack and defense when applicable), and emit `[ESTADO_COMBATE]` at the end of every combat turn. The GM SHALL NOT narrate hit, miss, dodge, wound, or knockdown outcomes before the backend returns `[RESULTADO DO SISTEMA]` for each emitted test.

#### Scenario: Player combat turn with attack

- **WHEN** it is the player's turn in combat and the player declares an attack
- **THEN** the GM emits a `[TESTE]` with `tipo` `ataque_cc` or `ataque_distancia` as appropriate
- **AND** waits for the roll result before narrating hit or miss
- **AND** if the attack hits and the target can react, emits a defensive `[TESTE]` (`teste_atributo` with skill `Esquivar` or melee parry) before narrating final damage
- **AND** emits `[ESTADO_COMBATE]` after turn resolution

#### Scenario: Enemy attacks the player

- **WHEN** it is an enemy's turn and the enemy attacks the player character
- **THEN** the GM emits an enemy attack `[TESTE]` first
- **AND** if the attack succeeds, emits a player defensive `[TESTE]` (typically `Esquivar`) before narrating whether the blow lands
- **AND** does NOT narrate wounding prose without both roll results when defense is possible

#### Scenario: GM must not skip combat rolls

- **WHEN** combat is active and a strike or defensive reaction is being resolved
- **THEN** the GM does NOT resolve the exchange purely in narrative prose
- **AND** always emits `[TESTE]` and waits for the backend

---

## ADDED Requirements

### Requirement: GM MUST emit tests for mandatory situational triggers

When the narrative or player action matches a mandatory situational trigger, the GM SHALL emit a `[TESTE]` signal and pause resolution until the backend returns the roll result. The GM SHALL NOT narrate the contested outcome before the test completes.

#### Scenario: Chase after fleeing NPC

- **GIVEN** the GM narrated that an NPC began running away from the player
- **WHEN** the player pursues or the situation requires resolving whether the player catches up
- **THEN** the GM emits `[TESTE]` with skill `Atletismo` (Agility) and contextual modifier
- **AND** narrates catch or failure only after `[RESULTADO DO SISTEMA]`
- **AND** does NOT narrate catching the NPC by the collar without a roll

#### Scenario: Player declares stealthy entry

- **GIVEN** the player declares intent to enter, move, or hide stealthily (e.g. "quero entrar furtivamente")
- **WHEN** success or failure of remaining undetected is uncertain and matters
- **THEN** the GM emits `[TESTE]` with skill `Furtividade`
- **AND** waits for the result before narrating detection or safe passage
- **AND** does NOT narrate unobserved entry without a roll

#### Scenario: Trivial action still exempt

- **GIVEN** the player performs a trivial action with no meaningful failure consequence (e.g. opening an unlocked door)
- **WHEN** the action matches the general "no test required" criteria in the GM prompt
- **THEN** the GM MAY narrate without `[TESTE]`
- **AND** mandatory triggers (chase, stealth, combat) do NOT apply
