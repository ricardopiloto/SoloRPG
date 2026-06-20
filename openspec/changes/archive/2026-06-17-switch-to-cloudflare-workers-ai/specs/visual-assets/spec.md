## MODIFIED Requirements

### Requirement: Asynchronous Scene Image Generation
When the GM emits `[IMAGEM]`, the system SHALL queue image generation asynchronously via Cloudflare Workers AI using model `@cf/black-forest-labs/flux-1-schnell` and configured `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_API_TOKEN`. Image generation SHALL NOT block narrative text delivery. Placeholders SHALL display until the image job completes.

#### Scenario: Scene image requested during narration
- **WHEN** the GM emits `[IMAGEM]` with tipo "cena" during a turn
- **THEN** the narrative text streams to the player immediately
- **AND** a background image job is created with status `pending`
- **AND** the UI displays a thematic placeholder until the image URL is available

#### Scenario: Cloudflare generation completes
- **WHEN** Cloudflare Workers AI returns a base64-encoded image
- **THEN** the backend persists the image and sets job status to `completed`
- **AND** the frontend replaces the placeholder with the scene illustration inline in the chat via polling `GET /api/images/{job_id}`

#### Scenario: Cloudflare unavailable or misconfigured
- **WHEN** `CLOUDFLARE_ACCOUNT_ID` or `CLOUDFLARE_API_TOKEN` is missing, or the API returns an error
- **THEN** the job status becomes `failed` or falls back to a thematic placeholder
- **AND** narrative delivery is unaffected

### Requirement: Visual Inventory
The system SHALL display character trappings/inventory with visual representations. Item-type images from `[IMAGEM]` tipo "item" SHALL be linked to inventory entries when available.

#### Scenario: Item illustration linked
- **WHEN** a significant item image is generated via Cloudflare Workers AI
- **THEN** the inventory panel shows the image alongside the item record

### Requirement: Image Job Status API
The system SHALL expose an endpoint to poll image job status and URL for the frontend.

#### Scenario: Frontend polls pending image
- **WHEN** the frontend receives an image job_id from a turn response
- **THEN** it polls until status is `completed` or `failed`
- **AND** updates inline display when URL becomes available

#### Scenario: Image file served by backend
- **WHEN** an image job is `completed`
- **THEN** `image_url` points to a stable backend route (`GET /api/images/{job_id}/file`)
- **AND** the frontend can render the image without expiring signed URLs

## REMOVED Requirements

### Requirement: BFL Flux 1.1 Pro Integration
**Reason**: Provider substituído por Cloudflare Workers AI (FLUX.1 Schnell) para alinhar documentação, custo e API síncrona.
**Migration**: Remover `flux_client.py`, `FLUX_API_KEY`, `FLUX_API_URL`; configurar `CLOUDFLARE_ACCOUNT_ID` e `CLOUDFLARE_API_TOKEN`.
