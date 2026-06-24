## MODIFIED Requirements

### Requirement: Semantic memory search
The system SHALL store narrative event embeddings in SQLite as JSON arrays. Semantic search SHALL rank events using in-process cosine similarity via `PythonSearchAdapter` and `simple_embedding`. External vector databases (pgvector) SHALL NOT be required.

#### Scenario: Semantic search on SQLite
- **WHEN** the GM orchestrator requests relevant memories for a campaign turn
- **THEN** the backend loads recent narrative events from SQLite
- **AND** ranks them by cosine similarity to the query embedding in Python
- **AND** returns the top N events for context injection

#### Scenario: No pgvector dependency
- **WHEN** the application starts
- **THEN** no PostgreSQL extension or pgvector package is loaded
- **AND** semantic memory functions without external vector infrastructure
