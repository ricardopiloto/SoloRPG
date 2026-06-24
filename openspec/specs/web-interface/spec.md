# web-interface Specification

## Purpose
TBD - created by archiving change fix-silent-api-failures. Update Purpose after archive.
## Requirements
### Requirement: Visible API error feedback on core pages
The home, campaigns, and character pages SHALL display a user-visible error message when initial data loading or create actions fail due to API errors, instead of failing silently with empty state.

#### Scenario: Load failure on campaigns page
- **WHEN** `GET /characters` or `GET /campaigns` fails
- **THEN** the campaigns page displays an error message explaining the failure
- **AND** the user is not left with an empty screen that appears functional

#### Scenario: Character creation failure
- **WHEN** the user clicks a pregen or submits custom character creation and the API returns an error
- **THEN** an error message is shown on the character page
- **AND** the user understands the action failed

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
The UI SHALL provide screens for creating and selecting characters and campaigns. These screens SHALL require authentication and SHALL display only resources belonging to the logged-in user.

#### Scenario: Character management access
- **WHEN** the authenticated player is not in an active session
- **THEN** they can access character and campaign management
- **AND** see only their own characters and related campaigns

#### Scenario: Unauthenticated management blocked
- **WHEN** an unauthenticated visitor tries to open character or campaign management
- **THEN** they are redirected to login

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
The character sheet side panel SHALL display Fate Points (current/max) and Fortune Points (current/max) as separate visible finite resources using gem indicators.

#### Scenario: Fate and Fortune display
- **WHEN** the player views the character sidebar during a session
- **THEN** Fate Points are shown as current/max gem indicators (◆ filled, ◇ empty)
- **AND** Fortune Points are shown as a separate current/max gem row below or beside Fate
- **AND** both update immediately after expenditure during the session

#### Scenario: Fortune spend prompt on failed test
- **WHEN** a GM-requested test fails and the character has Fortune Points remaining
- **THEN** the UI SHALL offer an option to spend a Fortune Point to re-roll
- **AND** SHALL NOT offer a +10 bonus alternative

### Requirement: Authentication screens
The web interface SHALL provide dedicated screens for registration, email verification, and login. All user-facing copy SHALL be in PT-BR.

#### Scenario: Registration screen
- **WHEN** an unauthenticated visitor opens the registration screen
- **THEN** the UI presents fields for email, password, and password confirmation
- **AND** validates matching passwords before submit

#### Scenario: Verification screen after registration
- **WHEN** registration succeeds
- **THEN** the user is directed to enter the 8-digit email verification code
- **AND** can request code resend with visible rate-limit feedback

#### Scenario: Login screen
- **WHEN** an unauthenticated visitor opens the login screen
- **THEN** the UI presents email and password fields
- **AND** links to registration for new users

### Requirement: Protected application routes
Pages that access user-specific game data SHALL require authentication. Unauthenticated visitors SHALL be redirected to the login screen.

#### Scenario: Redirect when not logged in
- **WHEN** an unauthenticated user navigates to home, character management, or campaigns
- **THEN** the frontend redirects to login
- **AND** preserves intended destination for post-login redirect when practical

#### Scenario: Authenticated access to game data
- **WHEN** a logged-in user navigates to home or character management
- **THEN** the UI loads data scoped to their account

### Requirement: Logout
The interface SHALL allow the authenticated user to log out, clearing the local session token and returning to the login screen.

#### Scenario: User logs out
- **WHEN** the user clicks logout
- **THEN** the stored auth token is cleared
- **AND** subsequent API calls do not send Authorization
- **AND** protected routes redirect to login

### Requirement: UI MUST show fortune re-roll prompt on failed test

After a failed GM-requested test, the UI SHALL offer at most one Fortune re-roll while `fortune_reroll_available` is true.

- **WHEN** a GM-requested test fails and the character has Fortune Points remaining **and** Fortune has not yet been spent on that test instance (`fortune_reroll_available = true`)
- **THEN** the UI SHALL offer an option to spend a Fortune Point to re-roll once
- **AND** SHALL NOT offer a +10 bonus alternative

#### Scenario: No prompt after fortune already used on test

- **WHEN** the player failed a test, spent Fortune to re-roll once, and failed again
- **THEN** the UI SHALL NOT show the Fortune re-roll button again for that test
- **AND** SHALL show only the option to continue with the failed result

