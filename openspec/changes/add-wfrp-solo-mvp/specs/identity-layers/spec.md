## ADDED Requirements

### Requirement: Karma Tracking
The system SHALL track an internal karma score from -100 to 100 per character. Karma SHALL be updated via karma_delta from `[FIM_SESSAO]` resumo_sistema. Karma SHALL NOT be displayed as a numeric value in the UI.

#### Scenario: Karma delta after moral decision
- **WHEN** a session ends with karma_delta of +5
- **THEN** the system adds 5 to the character's karma score (clamped to -100..100)
- **AND** injects the updated karma value in `<personagem><karma>` for LLM context only
- **AND** does NOT show karma numbers in the player UI

### Requirement: Faction Reputation Tracking
The system SHALL track reputation scores from -100 to 100 per faction per campaign. Reputation SHALL be updated via reputacao_delta from `[FIM_SESSAO]`. Reputation SHALL NOT be displayed as numeric values in the UI.

#### Scenario: Reputation increase with faction
- **WHEN** a session ends with reputacao_delta {"Guilda dos Estivadores": +10}
- **THEN** the system updates the faction reputation score
- **AND** injects `<personagem><reputacao>` for LLM context
- **AND** reveals effects only through narrative world reactions

### Requirement: Social Perception
The system SHALL maintain a descriptive social perception field (percepcao_social) representing how NPCs and groups currently view the character. This field SHALL be updated based on narrative events and injected into LLM context.

#### Scenario: Perception after public act
- **WHEN** the character performs a publicly visible heroic act
- **THEN** the system updates percepcao_social text (e.g., "visto como herói local")
- **AND** injects the description in `<personagem><percepcao_social>`
- **AND** does NOT display a numeric perception score

### Requirement: Automatic Character Diary
The system SHALL automatically generate the character diary from session resumo_jogador texts. The diary SHALL be read-only for the player.

#### Scenario: Diary entry after session
- **WHEN** a session ends with resumo_jogador
- **THEN** the system appends the summary as a new diary entry with session date
- **AND** presents it in the diary panel as read-only narrative log

#### Scenario: Player attempts to edit diary
- **WHEN** the player views the diary panel
- **THEN** no edit controls are available
- **AND** entries are displayed as chronological narrative log

### Requirement: Narrative-Only Identity Revelation
Karma, reputation, and social perception effects SHALL manifest only through GM narration and NPC behavior (tone changes, open/closed doors, world reactions), never through numeric UI indicators.

#### Scenario: Low reputation with faction
- **WHEN** the character has low reputation with a faction
- **THEN** the UI shows no reputation number
- **AND** the GM narrates NPCs refusing service or hostile tone when the player interacts with that faction
