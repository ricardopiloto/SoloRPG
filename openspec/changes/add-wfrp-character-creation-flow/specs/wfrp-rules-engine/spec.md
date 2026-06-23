## ADDED Requirements

### Requirement: Character creation validation API
The backend SHALL expose read endpoints for creation options and careers and a validation endpoint that returns computed preview stats without persisting.

#### Scenario: Creation options endpoint
- **WHEN** the client requests `GET /rules/character-creation`
- **THEN** the response includes species available for creation, XP award tables, attribute method rules, and skill allocation limits

#### Scenario: Validate draft without persist
- **WHEN** the client posts a partial or complete `CharacterCreationDraft` to `POST /characters/validate-creation`
- **THEN** the backend returns validation errors and a `computed` preview (attributes, wounds, fate, skills, XP totals) without writing to the database

#### Scenario: Persist validated character
- **WHEN** the client posts a complete validated `CharacterCreationSubmit` to `POST /characters`
- **THEN** the backend persists the character with all derived values
- **AND** returns `CharacterOut` identical in shape to existing characters

### Requirement: Background generation endpoint
The backend SHALL expose `POST /characters/generate-background` that accepts a creation-draft snapshot and returns generated background prose only.

#### Scenario: Background generation request
- **WHEN** the client posts `BackgroundGenerateRequest` with name, career, and optional species, talents, skills summary, and hints
- **THEN** the backend invokes the LLM adapter with the character-background system prompt
- **AND** returns `{ background: string }` without persisting a character record

#### Scenario: Background generation uses non-GM prompt
- **WHEN** background generation is invoked
- **THEN** the GM system prompt (`gm-system-prompt.md`) is not used
- **AND** the dedicated character-background prompt is used instead
