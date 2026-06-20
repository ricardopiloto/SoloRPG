## ADDED Requirements

### Requirement: Campaign Lifecycle States
Each campaign SHALL have one of the following statuses: active (ativa), completed (concluída), or unfinished (inacabada — death or abandonment without resolution).

#### Scenario: Campaign completed
- **WHEN** the central narrative objective is resolved
- **THEN** the system marks the campaign status as concluída
- **AND** preserves full history including sessions, NPCs, and events

#### Scenario: Campaign unfinished by death
- **WHEN** the player character dies permanently
- **THEN** the system marks the campaign status as inacabada
- **AND** preserves the campaign record without deletion
- **AND** records the death cause from `[ACAO_SISTEMA]` morte_personagem

### Requirement: Campaign Creation on First Session
The first session of a new campaign SHALL trigger GM campaign generation. The system SHALL persist data from `[NOVA_CAMPANHA]`: tone, opening location, initial hook, secret objective, antagonist, initial NPCs, and estimated session duration.

#### Scenario: First session campaign bootstrap
- **WHEN** a player starts their first session on a new campaign
- **THEN** the backend sets `{primeira_sessao: true}` in LLM context
- **AND** persists `[NOVA_CAMPANHA]` payload to the campaigns table
- **AND** creates initial NPC records from npcs_iniciais

### Requirement: Campaign Continuation
The player SHALL resume an active campaign from the last saved narrative state with the same character and preserved context.

#### Scenario: Continue active campaign
- **WHEN** the player selects an active campaign to continue
- **THEN** the system loads campaign state, character, memory summaries, and last session position
- **AND** starts a new session with `{primeira_sessao: false}`

### Requirement: New Campaign After Completion or Death
After campaign completion or character death, the player SHALL choose to either continue with the same living character in a new story or create a new character from scratch.

#### Scenario: New campaign with existing living character
- **WHEN** the player completes a campaign and chooses to continue the same character
- **THEN** the system creates a new campaign linked to the existing character
- **AND** triggers first-session campaign generation with `{primeira_sessao: true}`

#### Scenario: New campaign with new character
- **WHEN** the player chooses to start fresh after death or completion
- **THEN** the system presents character creation or pre-generated selection
- **AND** creates a new campaign with the new character

### Requirement: Campaign History
The system SHALL display a history of all campaigns grouped by status (active, completed, unfinished).

#### Scenario: View campaign history
- **WHEN** the player opens campaign management
- **THEN** the UI lists campaigns with status, character name, and last session date
- **AND** unfinished campaigns remain accessible as preserved stories without conclusion

### Requirement: Secret Campaign Objectives
Campaign secret objectives and antagonist details SHALL be stored server-side and injected into LLM context but NEVER exposed directly to the player in the UI.

#### Scenario: Player inspects campaign details
- **WHEN** the player views campaign information in the UI
- **THEN** secret objectives and antagonist secrets are not displayed
- **AND** only player-visible narrative summaries are shown
