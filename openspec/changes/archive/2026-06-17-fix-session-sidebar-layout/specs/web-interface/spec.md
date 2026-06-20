## MODIFIED Requirements

### Requirement: Session Layout
The UI SHALL provide a central chat panel for GM narration and player input, with side panels for character sheet, visual inventory, map, and diary. During an active session, the left and right side panels SHALL remain fixed in the viewport and SHALL NOT scroll when the chat history scrolls. Only the central chat history area SHALL have vertical scroll. Side panels MAY have independent internal scroll when their own content exceeds viewport height.

#### Scenario: Active session layout
- **WHEN** the player is in an active session
- **THEN** the chat panel occupies the central area
- **AND** side panels display ficha, inventário, mapa, and diário
- **AND** all panels are accessible without leaving the session

#### Scenario: Long chat history scroll
- **WHEN** the player scrolls through a long GM narration history in the chat
- **THEN** the left panel (character sheet and inventory) remains fixed in viewport position
- **AND** the right panel (map and diary) remains fixed in viewport position
- **AND** the session header and text input remain visible without scrolling the page body

#### Scenario: Long diary content
- **WHEN** the diary panel contains more entries than fit on screen
- **THEN** the diary panel scrolls internally within its fixed sidebar
- **AND** the chat panel scroll position is not affected

#### Scenario: Viewport height constraint
- **WHEN** the session view is rendered on desktop (≥ 1024px width)
- **THEN** the session layout uses the full viewport height (`100vh` or `100dvh`)
- **AND** the document body does not scroll during an active session
