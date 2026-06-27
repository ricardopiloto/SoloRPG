# Spec delta: visual-assets

**Change:** `switch-to-openrouter-images`

---

## MODIFIED Requirements

### Requirement: Asynchronous Scene Image Generation

When the GM emits `[IMAGEM]`, the system SHALL queue image generation asynchronously via **OpenRouter Image API** using model `black-forest-labs/flux.2-klein-4b` (configurable via `OPENROUTER_IMAGE_MODEL`) and `OPENROUTER_API_KEY`. Image generation SHALL NOT block narrative text delivery to the player.

#### Scenario: Scene image requested during narration

- **WHEN** the GM emits `[IMAGEM]` with tipo "cena" during a turn
- **THEN** the narrative text streams to the player immediately
- **AND** image generation runs in a background queue calling `POST https://openrouter.ai/api/v1/images`
- **AND** the UI displays a thematic placeholder until the image job completes

#### Scenario: Image generation completes

- **WHEN** OpenRouter returns `data[].b64_json` for the job
- **THEN** the backend decodes base64, saves the file, and exposes it via `/api/images/{id}/file`
- **AND** the UI replaces the placeholder with the scene illustration
- **AND** caches the image URL linked to the campaign/session

#### Scenario: OpenRouter not configured

- **WHEN** `OPENROUTER_API_KEY` is missing or empty
- **THEN** the image client SHALL report `enabled=false`
- **AND** jobs SHALL fail without calling the external API (per session-image-credits-guard probe behavior)

#### Scenario: OpenRouter API error

- **WHEN** OpenRouter returns HTTP 4xx/5xx or a response without image data
- **THEN** the job SHALL be marked `failed` with `image_url=null`
- **AND** narrative delivery SHALL continue without a fallback placeholder image in the chat

---

**Migration note:** Replace Cloudflare Workers AI (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `flux-1-schnell`) with OpenRouter (`OPENROUTER_API_KEY`, `OPENROUTER_IMAGE_MODEL`). Remove `cloudflare_workers_ai.py`.
