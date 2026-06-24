# synthetic-gm Specification

## Purpose
TBD - created by archiving change add-wfrp-solo-mvp. Update Purpose after archive.
## Requirements
### Requirement: GM Persona Inviolável
The system SHALL inject the GM system prompt from `Docs/gm-system-prompt.md` as the LLM system message on every turn. The GM SHALL never break character, never reference AI/LLM/automation, and SHALL always respond in PT-BR regardless of player input language.

#### Scenario: Player asks if the GM is an AI
- **WHEN** the player asks "você é uma IA?" or similar meta question
- **THEN** the GM responds in-character with narrative rejection (the world does not respond as expected)
- **AND** the system does NOT emit a system error or meta-commentary message

#### Scenario: Player writes in English
- **WHEN** the player sends an action in English
- **THEN** the GM narrates the response in PT-BR
- **AND** maintains second-person present tense with sensory focus

### Requirement: Context Injection per Turn
The system SHALL assemble and inject structured context blocks before each player input: `<campanha>`, `<personagem>`, `<memoria>`, and `<sessao>` as defined in the GM system prompt.

#### Scenario: Turn during active exploration session
- **WHEN** the player submits an action during an active exploration session
- **THEN** the backend injects campaign tone, secret objective, world state, character sheet, memory summaries, semantic events, and session mode/time remaining
- **AND** the LLM receives the assembled context before the player message

### Requirement: Signal Protocol for Backend Actions
The GM LLM SHALL emit structured signals wrapped in delimited tags when mechanical resolution, image generation, session end, or campaign creation is required. Supported signals: `[TESTE]`, `[ACAO_SISTEMA]`, `[ESTADO_COMBATE]`, `[IMAGEM]`, `[NOVA_CAMPANHA]`, `[FIM_SESSAO]`.

#### Scenario: Skill test required
- **WHEN** the GM determines a player action requires an attribute or skill test
- **THEN** the GM emits a `[TESTE]` signal with JSON payload (tipo, atributo, pericia optional, modificador, descricao, consequencia_sucesso, consequencia_falha)
- **AND** pauses mechanical resolution until the backend returns the roll result
- **AND** does NOT invent the roll outcome

#### Scenario: Scene location change
- **WHEN** the scene changes location or a narratively significant moment occurs
- **THEN** the GM emits an `[IMAGEM]` signal with descricao, tipo (cena/personagem/mapa/item), and prioridade (normal/marco)

### Requirement: First Session Campaign Generation
When `{primeira_sessao: true}` is indicated by the backend, the GM SHALL define campaign tone, secret objective, antagonist, initial hooks, and starting NPCs internally, emit `[NOVA_CAMPANHA]` JSON for persistence, and begin narration immediately inside a scene without meta introduction.

#### Scenario: New campaign first session starts
- **WHEN** the backend signals first session for a new campaign
- **THEN** the GM emits `[NOVA_CAMPANHA]` with tom, localizacao_abertura, gancho_inicial, objetivo_secreto, antagonista, npcs_iniciais, and duracao_estimada_sessao_minutos
- **AND** begins narration with an immediate in-scene opening sentence
- **AND** does NOT reveal secret objectives to the player

### Requirement: Session End Summary
When `{encerrar_sessao: true}` or session time expires, the GM SHALL guide narrative to a natural pause point and emit `[FIM_SESSAO]` with resumo_jogador (3–5 paragraphs) and resumo_sistema (events, NPCs, decisions, world state, open hooks, karma/reputation deltas, xp_sugerido 30–100).

#### Scenario: Session time runs out during exploration
- **WHEN** the backend signals session end due to elapsed time
- **THEN** the GM narrates a natural stopping point (tavern, camp, pause moment)
- **AND** emits `[FIM_SESSAO]` with player-visible summary and system summary for persistence

### Requirement: Narrative Voice Standards
The GM SHALL narrate in second person, present tense, with short dense paragraphs, sensory descriptions, distinct NPC voices, implicit dilemmas without delivered solutions, and SHALL always end exploration turns with "O que você faz?".

#### Scenario: Exploration turn narration
- **WHEN** the GM completes an exploration narration segment
- **THEN** the text uses second person present tense
- **AND** ends with "O que você faz?" unless in combat mode

### Requirement: Combat Narration Protocol
In COMBATE mode, the GM SHALL announce whose turn it is, wait for player action on player turns, emit required `[TESTE]` signals for attacks, and emit `[ESTADO_COMBATE]` at the end of every combat turn.

#### Scenario: Player combat turn
- **WHEN** it is the player's turn in combat
- **THEN** the GM announces the turn owner
- **AND** waits for player action before resolving
- **AND** emits `[ESTADO_COMBATE]` after turn resolution with turn number, character/enemy status, and proxima_acao

### Requirement: LLM Response Streaming
The system SHALL stream GM narrative text to the frontend as it is generated to reduce perceived latency.

#### Scenario: Player submits action
- **WHEN** the player sends an action and the LLM begins generating a response
- **THEN** the frontend receives streamed text chunks before the full response completes

