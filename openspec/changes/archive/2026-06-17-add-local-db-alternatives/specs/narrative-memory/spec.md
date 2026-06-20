## MODIFIED Requirements

### Requirement: Semantic Vector Memory
The system SHALL store embeddings of narrative events and decisions. On PostgreSQL backends, embeddings SHALL use pgvector. On `sqlite-dev` profile, embeddings SHALL be stored as JSON and retrieved via in-process similarity search. On each turn, the system SHALL retrieve the N most relevant events for the current context using semantic similarity with metadata filters (campaign_id, recency, event type).

#### Scenario: Semantic event retrieval on PostgreSQL
- **WHEN** the player references a past decision in a long campaign on PostgreSQL
- **THEN** the backend queries pgvector for semantically related events
- **AND** injects top-N results as `<memoria><eventos_relevantes>` in LLM context
- **AND** filters results to the current campaign_id

#### Scenario: Semantic event retrieval on SQLite dev profile
- **WHEN** the player references a past decision on `sqlite-dev` profile
- **THEN** the backend retrieves events using in-process cosine similarity over stored JSON embeddings
- **AND** injects top-N results as `<memoria><eventos_relevantes>` in LLM context
- **AND** filters results to the current campaign_id

#### Scenario: Semantic search parity in dev
- **WHEN** the same campaign events exist on SQLite-dev and PostgreSQL profiles
- **THEN** both profiles return relevant events for the same query
- **AND** SQLite-dev may differ in ranking but SHALL not return empty results when matching events exist
