## ADDED Requirements

### Requirement: Structured Relational Memory
The system SHALL persist deterministic campaign facts in PostgreSQL: campaigns, sessions, player_characters, npcs, factions, events, and inventory references.

#### Scenario: Session event persistence
- **WHEN** a session ends with `[FIM_SESSAO]` resumo_sistema.eventos_principais
- **THEN** the system creates event records linked to the session and campaign
- **AND** updates NPC status and relationship changes from npcs_interagidos

### Requirement: Semantic Vector Memory
The system SHALL store embeddings of narrative events and decisions in pgvector. On each turn, the system SHALL retrieve the N most relevant events for the current context using semantic similarity with metadata filters (campaign_id, recency, event type).

#### Scenario: Semantic event retrieval
- **WHEN** the player references a past decision in a long campaign
- **THEN** the backend queries pgvector for semantically related events
- **AND** injects top-N results as `<memoria><eventos_relevantes>` in LLM context
- **AND** filters results to the current campaign_id

### Requirement: Compressed Session Summaries
At session end, the system SHALL persist the LLM-generated resumo_sistema from `[FIM_SESSAO]` as compressed technical summary. The resumo_jogador SHALL be stored separately for player-visible diary and session recap.

#### Scenario: Session summary feeds next session
- **WHEN** a new session starts for an existing campaign
- **THEN** the backend injects `<memoria><ultimas_sessoes>` with summaries from the last N sessions
- **AND** injects `<memoria><resumo_da_campanha>` with compressed campaign-level summary

### Requirement: Active Session Context Window
The system SHALL assemble a four-layer context for each LLM turn: (1) system prompt, (2) campaign + character structured state, (3) compressed summaries + semantic events + active NPCs/hooks, (4) active session recent turn history and player input.

#### Scenario: Context assembly for turn 50 of session
- **WHEN** the player submits turn 50 in an active session
- **THEN** the context includes system prompt, campaign/personagem blocks, memory layers, and last K session turns
- **AND** does NOT include the full raw transcript of all prior sessions

### Requirement: NPC and Hook Tracking
The system SHALL maintain active NPC records (name, faction, relationship, status) and pending narrative hooks (ganchos_pendentes) updated from session summaries.

#### Scenario: NPC relationship change
- **WHEN** `[FIM_SESSAO]` reports an NPC status_relacao change to "hostil"
- **THEN** the system updates the NPC record
- **AND** injects updated NPC list in `<memoria><npcs_ativos>` on subsequent turns

#### Scenario: Open hook persistence
- **WHEN** `[FIM_SESSAO]` includes ganchos_abertos
- **THEN** the system persists unresolved hooks
- **AND** injects them as `<memoria><ganchos_pendentes>` until resolved in a future session

### Requirement: World State Updates
The system SHALL persist world state changes from `[FIM_SESSAO]` resumo_sistema.estado_mundo and inject current world state in `<campanha><estado_do_mundo>` on each turn.

#### Scenario: World state after session
- **WHEN** a session ends with estado_mundo describing a city under suspicion
- **THEN** the system updates the campaign world_state field
- **AND** subsequent sessions reflect the updated state in LLM context
