## MODIFIED Requirements

### Requirement: Semantic Vector Memory
The system SHALL store embeddings of narrative events. On PostgreSQL backends, the system SHALL query pgvector using SQL similarity search with campaign_id filters. On sqlite-dev profile, the system SHALL use in-process similarity fallback.

#### Scenario: Semantic event retrieval on PostgreSQL
- **WHEN** the player references a past decision on PostgreSQL
- **THEN** the backend queries pgvector with SQL ORDER BY embedding <=> query
- **AND** injects top-N results as `<memoria><eventos_relevantes>`

## MODIFIED Requirements

### Requirement: Social Perception
The system SHALL maintain a descriptive social perception field updated from session summaries and narrative events in `[FIM_SESSAO]` resumo_sistema.

#### Scenario: Perception updated after session
- **WHEN** `[FIM_SESSAO]` includes social perception change in resumo_sistema
- **THEN** the system updates character.social_perception text
- **AND** injects updated text in subsequent LLM context
