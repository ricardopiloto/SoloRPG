# session-orchestration Specification

## Purpose
TBD - created by archiving change add-wfrp-solo-mvp. Update Purpose after archive.
## Requirements
### Requirement: Session Duration Announcement
Before each session begins, the system SHALL display the estimated session duration to the player. Sessions SHALL NOT be pausable once started.

#### Scenario: Session start
- **WHEN** the player starts a new session
- **THEN** the UI shows estimated duration in minutes (from `[NOVA_CAMPANHA]` or campaign defaults)
- **AND** informs the player the session cannot be paused
- **AND** begins the session timer upon confirmation

### Requirement: Exploration Mode
The default session mode SHALL be EXPLORACAO. The system SHALL track remaining time in minutes, display a visible timer, and inject `<sessao><modo>EXPLORACAO</modo><tempo_restante>` into the LLM context.

#### Scenario: Exploration with time remaining
- **WHEN** the session is in exploration mode with 15 minutes remaining
- **THEN** the UI displays the countdown timer
- **AND** the LLM receives tempo_restante for narrative pacing calibration

#### Scenario: Exploration time nearly expired
- **WHEN** less than 5 minutes remain in exploration mode
- **THEN** the backend may signal `{encerrar_sessao: true}` to the LLM
- **AND** the LLM guides narrative toward a natural pause point

### Requirement: Combat Mode
When direct physical confrontation begins, the system SHALL switch to COMBATE mode. The system SHALL roll initiative (Agility + d10) server-side, manage turn order, display turn counter, and inject `<sessao><modo>COMBATE</modo><turno_de_combate>` into context.

#### Scenario: Combat initiated
- **WHEN** the narrative triggers physical confrontation
- **THEN** the backend switches session mode to COMBATE
- **AND** rolls initiative for all combatants server-side
- **AND** displays turn order and current turn in the UI

#### Scenario: Combat turn progression
- **WHEN** a combat turn resolves
- **THEN** the system advances to the next combatant in initiative order
- **AND** increments the turn counter
- **AND** waits for player input only on the player's turn

### Requirement: Combat End Conditions
Combat SHALL end when all enemies are defeated or flee, or when the character falls or flees. The system SHALL return to EXPLORACAO mode after combat ends unless session time has expired.

#### Scenario: All enemies defeated
- **WHEN** all enemies are defeated or have fled
- **THEN** the system ends combat mode
- **AND** switches back to EXPLORACAO mode
- **AND** resumes exploration time tracking

### Requirement: Active Session Turn History
The system SHALL persist the last K turns of the active session and inject them as `<sessao><historico_recente>` for LLM context.

#### Scenario: Mid-session context assembly
- **WHEN** the player submits an action during an active session
- **THEN** the backend includes the last K turns of player actions and GM responses in session context
- **AND** excludes turns from previous sessions from this block

### Requirement: Natural Session Save Point
When a session ends (time expired or narrative conclusion), the system SHALL save full campaign and character state at a narratively natural pause point, not mid-action.

#### Scenario: Session ends at narrative pause
- **WHEN** the session ends via time expiration or GM `[FIM_SESSAO]`
- **THEN** the system persists session summary, character state, and world state
- **AND** the next session resumes from the saved narrative position

### Requirement: Fortune refresh on session start
When a new game session is created, the system SHALL initialize Fortune Points from the character's current Fate Points before the first turn.

#### Scenario: New session initializes Fortune from Fate
- **WHEN** `start_session()` creates a new `GameSession` (not returning a paused session)
- **THEN** the character's `fortune_current` and `fortune_max` are set to `fate_current`
- **AND** the values are persisted before gameplay begins

#### Scenario: Paused session resume skips Fortune refresh
- **WHEN** `start_session()` returns an existing paused active session
- **THEN** Fortune Points are not recalculated from Fate Points

