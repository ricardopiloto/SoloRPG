## ADDED Requirements

### Requirement: DeepSeek as Default LLM Provider
The system SHALL use DeepSeek as the default LLM provider for GM narration. Configuration SHALL use `LLM_PROVIDER=deepseek`, `DEEPSEEK_API_KEY`, and `LLM_MODEL` (default `deepseek-chat`).

#### Scenario: Backend starts with default config
- **WHEN** no `LLM_PROVIDER` is set in environment
- **THEN** the system uses DeepSeek adapter
- **AND** connects to `https://api.deepseek.com/v1/chat/completions`

#### Scenario: DeepSeek API call for GM turn
- **WHEN** the player submits an action during an active session
- **THEN** the backend sends the GM system prompt and assembled context to DeepSeek
- **AND** receives narrative text and signal tags for backend processing

### Requirement: Real LLM Streaming via DeepSeek
The system SHALL stream GM narrative text from DeepSeek to the frontend using server-sent events (SSE) or equivalent streaming HTTP.

#### Scenario: Streaming narration to player
- **WHEN** DeepSeek begins generating a GM response
- **THEN** the frontend receives text chunks as they arrive from the API
- **AND** displays partial narration before the full response completes

## MODIFIED Requirements

### Requirement: LLM Response Streaming
The chat panel SHALL display GM narrative text as it streams from the backend. Streaming SHALL originate from the DeepSeek API response, not from simulated word splitting after a complete response.

#### Scenario: Streaming narration
- **WHEN** the GM response is being generated via DeepSeek
- **THEN** the chat panel shows partial text as API chunks arrive
- **AND** indicates when generation is in progress
