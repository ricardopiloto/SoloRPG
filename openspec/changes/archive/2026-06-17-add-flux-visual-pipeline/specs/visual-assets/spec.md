## MODIFIED Requirements

### Requirement: Asynchronous Scene Image Generation
When the GM emits `[IMAGEM]`, the system SHALL queue image generation asynchronously via Flux 1.1 Pro using configured `FLUX_API_KEY`. Image generation SHALL NOT block narrative text delivery. Placeholders SHALL display until the Flux job completes.

#### Scenario: Scene image requested during narration
- **WHEN** the GM emits `[IMAGEM]` with tipo "cena" during a turn
- **THEN** the narrative text streams to the player immediately
- **AND** a background Flux job is created with status `pending`
- **AND** the UI displays a thematic placeholder until the image URL is available

#### Scenario: Flux job completes
- **WHEN** the Flux API returns a generated image URL
- **THEN** the image job status becomes `completed`
- **AND** the frontend replaces the placeholder with the scene illustration inline in the chat

### Requirement: Visual Inventory
The system SHALL display character trappings/inventory with visual representations. Item-type images from Flux `[IMAGEM]` tipo "item" SHALL be linked to inventory entries when available.

#### Scenario: Item illustration linked
- **WHEN** a significant item image is generated
- **THEN** the inventory panel shows the image alongside the item record

## ADDED Requirements

### Requirement: Image Job Status API
The system SHALL expose an endpoint to poll image job status and URL for the frontend.

#### Scenario: Frontend polls pending image
- **WHEN** the frontend receives an image job_id from a turn response
- **THEN** it polls until status is `completed` or `failed`
- **AND** updates inline display when URL becomes available
