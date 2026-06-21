## ADDED Requirements

### Requirement: Session-level image generation guard

The visual assets pipeline SHALL respect the session-level `images_enabled` flag before enqueueing new image generation jobs from GM `[IMAGEM]` signals.

#### Scenario: No job enqueued when session images disabled

- **WHEN** the GM emits `[IMAGEM]` during a session with `images_enabled=false`
- **THEN** the system SHALL NOT enqueue a new image generation job
- **AND** narrative text delivery SHALL continue without visual interruption

#### Scenario: Jobs enqueued when session images enabled

- **WHEN** the GM emits `[IMAGEM]` during a session with `images_enabled=true`
- **THEN** the system SHALL enqueue image generation per existing asynchronous visual assets behavior
- **AND** narrative text SHALL NOT block on image completion
