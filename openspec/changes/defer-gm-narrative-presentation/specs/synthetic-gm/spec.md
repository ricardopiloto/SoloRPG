# Spec delta: synthetic-gm

**Change:** `defer-gm-narrative-presentation`

---

## MODIFIED Requirements

### Requirement: LLM Response Streaming

The system SHALL stream GM response generation over SSE to keep the connection alive and reduce time-to-first-byte processing on the server. **Player-visible chat MUST NOT render raw streamed tokens** — only the sanitized `narrative` from the `done` payload is displayed.

#### Scenario: Player submits action

- **WHEN** the player sends an action and the LLM begins generating a response
- **THEN** the frontend MAY receive SSE `token` events internally
- **AND** the chat displays "Preparando a resposta…" until `done`
- **AND** the player-visible narrative appears only once in the final `done.narrative`

#### Scenario: Transport streaming without player-facing partial text

- **WHEN** SSE `token` events arrive
- **THEN** the backend continues to emit them (unless later optimized)
- **AND** the frontend ignores them for `ChatLog` narrative rendering
