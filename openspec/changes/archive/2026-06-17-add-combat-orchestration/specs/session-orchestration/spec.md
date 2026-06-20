## MODIFIED Requirements

### Requirement: Combat Mode
When direct physical confrontation begins, the system SHALL switch to COMBATE mode. The system SHALL roll initiative (Agility + d10) server-side, manage turn order, display turn counter, and inject `<sessao><modo>COMBATE</modo><turno_de_combate>` into context. The GM orchestrator SHALL process `[ESTADO_COMBATE]` signals each combat turn.

#### Scenario: Combat initiated
- **WHEN** the narrative triggers physical confrontation or the GM emits combat state
- **THEN** the backend switches session mode to COMBATE
- **AND** rolls initiative for all combatants server-side
- **AND** displays turn order and current turn in the UI

#### Scenario: Combat turn progression
- **WHEN** a combat turn resolves and `[ESTADO_COMBATE]` is processed
- **THEN** the system advances to the next combatant in initiative order
- **AND** increments the turn counter
- **AND** waits for player input only on the player's turn

### Requirement: Combat Narration Protocol
In COMBATE mode, the GM SHALL announce whose turn it is, wait for player action on player turns, emit required `[TESTE]` signals for attacks, and emit `[ESTADO_COMBATE]` at the end of every combat turn. The backend SHALL synchronize session combat state with each `[ESTADO_COMBATE]` payload.

#### Scenario: ESTADO_COMBATE processed
- **WHEN** the GM emits `[ESTADO_COMBATE]` at end of a combat turn
- **THEN** the backend updates persisted combat_state on the session
- **AND** injects updated state in the next LLM context assembly

## MODIFIED Requirements

### Requirement: Session Timer Display
During exploration mode, the UI SHALL display a visible countdown timer showing remaining session minutes. During combat mode, the UI SHALL display the current combat turn number and active combatant in the left sidebar session status area.

#### Scenario: Combat turn counter visible
- **WHEN** the session is in COMBATE mode
- **THEN** the left sidebar shows the current combat turn number
- **AND** indicates whose turn is active
