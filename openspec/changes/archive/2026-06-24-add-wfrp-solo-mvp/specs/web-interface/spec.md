## ADDED Requirements

### Requirement: Text-Only Player Input
The player SHALL interact with the game exclusively via free-text input. The UI SHALL NOT provide videogame-style action controls (click-to-move, ability buttons, keyboard action shortcuts beyond typing).

#### Scenario: Player submits action
- **WHEN** the player types an action in the chat input and submits
- **THEN** the text is sent to the backend as the sole player action
- **AND** no alternative input mechanisms exist for in-game actions

### Requirement: Session Layout
The UI SHALL provide a central chat panel for GM narration and player input, with side panels for character sheet, visual inventory, map, and diary.

#### Scenario: Active session layout
- **WHEN** the player is in an active session
- **THEN** the chat panel occupies the central area
- **AND** side panels display ficha, inventário, mapa, and diário
- **AND** all panels are accessible without leaving the session

### Requirement: Dice Roll Animation
When the backend resolves a `[TESTE]` roll, the UI SHALL display a dice roll animation and the numeric result BEFORE the GM narrates the consequence.

#### Scenario: Visible dice roll sequence
- **WHEN** the backend completes a d100 roll for a skill test
- **THEN** the UI animates the dice roll
- **AND** displays the result (roll value, target, success/failure level)
- **AND** only then displays the GM's narrative consequence text

### Requirement: Session Timer Display
During exploration mode, the UI SHALL display a visible countdown timer showing remaining session minutes. During combat mode, the UI SHALL display the current combat turn number.

#### Scenario: Exploration timer visible
- **WHEN** the session is in EXPLORACAO mode
- **THEN** the UI shows remaining time in minutes
- **AND** updates the countdown in real time

#### Scenario: Combat turn counter visible
- **WHEN** the session is in COMBATE mode
- **THEN** the UI shows the current combat turn number
- **AND** indicates whose turn is active

### Requirement: Session End Screen
When a session ends, the UI SHALL display the resumo_jogador narrative summary and XP awarded before returning to campaign management or progression screens.

#### Scenario: Session recap display
- **WHEN** a session ends successfully
- **THEN** the UI shows the 3–5 paragraph player summary
- **AND** displays XP gained for the session
- **AND** offers navigation to character progression or campaign home

### Requirement: Campaign and Character Management Screens
The UI SHALL provide screens for: creating/selecting characters, viewing campaign history (active/completed/unfinished), starting/continuing sessions, and spending XP between sessions.

#### Scenario: Campaign home navigation
- **WHEN** the player is not in an active session
- **THEN** the UI presents options to continue an active campaign, start a new campaign, manage character progression, or view campaign history

### Requirement: Portuguese Brazil Native UI
All user-facing interface text SHALL be in PT-BR. The codebase SHALL use an i18n-ready structure (next-intl) to support future localization without refactoring.

#### Scenario: Interface language
- **WHEN** the player navigates any screen
- **THEN** all labels, buttons, messages, and system UI text are in PT-BR
- **AND** string resources are externalized for i18n

### Requirement: LLM Response Streaming Display
The chat panel SHALL display GM narrative text as it streams from the backend, character by character or chunk by chunk.

#### Scenario: Streaming narration
- **WHEN** the GM response is being generated
- **THEN** the chat panel shows partial text as it arrives
- **AND** indicates when generation is in progress

### Requirement: Fate Points on Character Sheet Panel
The character sheet side panel SHALL display Fate Points (current/max) as a visible finite resource.

#### Scenario: Fate Points display
- **WHEN** the player views the character sheet panel
- **THEN** Fate Points are shown as current/max values
- **AND** update immediately after Fate Point expenditure during a session
