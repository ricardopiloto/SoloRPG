## ADDED Requirements

### Requirement: WFRP Design System
The frontend SHALL use the grimório design tokens defined in `Docs/ux-spec.md` and the Open Design prototype `shared.css`: background `#0D0B08`, accent `#C9973A`, Cinzel for headings, Crimson Text for narrative prose, and Source Sans 3 for UI controls.

#### Scenario: Theme applied globally
- **WHEN** any application screen loads
- **THEN** background, surface, and accent colors match the WFRP token palette
- **AND** narrative text uses a serif display font distinct from UI labels

### Requirement: Multi-Screen Application Routes
The frontend SHALL provide distinct routes for each prototype screen: home (`/`), landing (`/landing`), character creation (`/character`), campaign hub (`/campaigns`), active session (`/play/[sessionId]`), session end (`/session/end`), progression (`/progression`), and character death (`/session/death`).

#### Scenario: Navigate from home to session
- **WHEN** the player selects an active campaign from home
- **THEN** the application navigates to `/play/[sessionId]`
- **AND** the session layout replaces the dashboard layout

#### Scenario: Session end flow
- **WHEN** a session ends successfully
- **THEN** the player is directed to `/session/end` with summary and XP
- **AND** CTAs offer progression or continue campaign

### Requirement: Session Prepare Overlay
Before the first turn of a session, the UI SHALL display a prepare overlay stating estimated duration (~45 min), that the session is not pausable, and a single CTA to begin.

#### Scenario: First visit to active session
- **WHEN** the player opens `/play/[sessionId]` for a new session
- **THEN** a modal overlay blocks interaction until confirmed
- **AND** after confirmation the overlay does not reappear for that session

### Requirement: Resizable Session Columns
The session screen SHALL provide draggable resize handles between the left sidebar, chat column, and right sidebar, persisting widths in browser storage.

#### Scenario: Resize left sidebar
- **WHEN** the player drags the left resize handle
- **THEN** the character sidebar width updates without breaking fixed scroll behavior
- **AND** the width is restored on next visit

### Requirement: Immersive Chat Presentation
During an active session, the central chat SHALL present GM narration as continuous prose blocks without messenger-style bubbles, user avatars, or visible timestamps. Player actions SHALL appear as subtle italic lines aligned to the right.

#### Scenario: GM narration display
- **WHEN** the GM narrates a scene
- **THEN** text appears as full-width prose in second person present tense
- **AND** no chat bubble borders or player/GM alignment styling is used

#### Scenario: Player action line
- **WHEN** the player submits an action
- **THEN** the action appears as an italic player-line block
- **AND** the input area remains a discrete bar at the bottom with icon send button

### Requirement: Inline Test Block
When the GM requests a test, the chat SHALL render an inline test card showing skill name, target number, a primary "Rolar dado" button, and an optional alternative action button.

#### Scenario: Test card displayed
- **WHEN** the backend signals a pending player test
- **THEN** a test-block card appears inline in the chat log
- **AND** dice roll animation does not start until the player clicks "Rolar dado"

### Requirement: Dice Overlay on Chat
Player-initiated d100 rolls SHALL display a centered dice overlay above the chat column (not inline in the message list), with a CSS 3D cube showing the result and screen-reader text for accessibility.

#### Scenario: Roll animation
- **WHEN** the player triggers a d100 roll from the test block
- **THEN** a dice overlay covers the chat area temporarily
- **AND** the numeric result is announced via aria-live

### Requirement: Character Sidebar Stats Layout
The left sidebar SHALL display: character identity, wounds bar (current/max), Fate Points as gem indicators (◆ filled, ◇ empty), collapsible skills/talents/inventory, session mode indicator, and session timer.

#### Scenario: Wounds bar visible
- **WHEN** the player views the left sidebar during a session
- **THEN** wounds are shown as a visual bar
- **AND** Fate Points are displayed as a finite gem resource

#### Scenario: Collapsible sections
- **WHEN** the player toggles skills or inventory sections
- **THEN** content expands or collapses in place without navigation

### Requirement: Dual Diary Sidebars
The right sidebar SHALL display separate read-only diary streams via tabs: campaign diary (session summaries) and character diary (personal perspective entries).

#### Scenario: Switch diary tab
- **WHEN** the player selects the Personagem tab
- **THEN** character-perspective diary entries are shown
- **AND** campaign diary entries are hidden

### Requirement: Session End and Death Screens
The application SHALL provide dedicated screens for normal session end (summary, XP, next steps) and character death (final narration, campaign marked unfinished, option to start new campaign).

#### Scenario: Character death
- **WHEN** the character dies (Fate Points exhausted)
- **THEN** the player is shown `/session/death` with narrative closure
- **AND** the campaign is marked as ended in campaign history

## MODIFIED Requirements

### Requirement: Session Layout
The UI SHALL provide a central immersive chat panel, a left sidebar for character stats (minimalist, numbers only), and a right sidebar for diaries (minimalist, read-only). Side panels SHALL remain fixed during chat scroll per `fix-session-sidebar-layout`. Layout and visual design SHALL match the Open Design prototype `game.html`.

#### Scenario: Active session layout
- **WHEN** the player is in an active session at `/play/[sessionId]`
- **THEN** the three-column layout matches prototype proportions and styling
- **AND** sidebars do not scroll with chat content
