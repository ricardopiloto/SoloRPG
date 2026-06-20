# Change: Pipeline Flux 1.1 Pro e ilustrações inline

## Why

`images.py` retorna apenas placeholders placehold.co. Product-brief v1.1 exige ilustrações Flux assíncronas inline na narrativa e mapas reveláveis com `image_url`.

## What Changes

- Fila assíncrona de jobs Flux 1.1 Pro (background task ou worker)
- Polling/SSE de status de imagem para frontend
- Render inline de cenas no chat
- Map regions com `image_url` real
- Cache por `cache_key` semântico

## Impact

- Affected specs: `visual-assets`, `web-interface`
- Affected code: `images.py`, `gm_orchestrator.py`, `routes.py`, `page.tsx`
