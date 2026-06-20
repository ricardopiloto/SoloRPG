# Change: Migrar geração de imagens para Cloudflare Workers AI

## Why

A documentação original (`Docs/session-flow.md`, `Docs/technical-research.md`) especifica **Cloudflare Workers AI (FLUX.1 Schnell)**, mas a implementação da Fase 4 (`add-flux-visual-pipeline`) usa **Black Forest Labs Flux 1.1 Pro** com polling assíncrono. Isso cria divergência de stack, credenciais (`FLUX_API_KEY` vs Cloudflare) e custo operacional.

Cloudflare Workers AI oferece:
- Alinhamento com a arquitetura já documentada
- API síncrona (resposta base64 em uma requisição — sem polling externo)
- Cota gratuita diária no tier Workers AI (adequada ao MVP pessoal)
- Mesmo modelo base (FLUX Schnell via `@cf/black-forest-labs/flux-1-schnell`)

## What Changes

- Substituir `FluxClient` (BFL `api.bfl.ai`) por `CloudflareWorkersAIClient`
- Novas variáveis: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`; remover `FLUX_API_KEY` / `FLUX_API_URL`
- Persistir imagens geradas (base64 → arquivo JPEG servido pelo backend) em vez de URLs temporárias BFL
- Manter pipeline existente: `ImageJob` (`pending → processing → completed|failed`), cache por `cache_key`, `GET /api/images/{job_id}`, `SceneImage` no frontend
- Atualizar testes com mock da API Cloudflare
- Atualizar `Docs/`, `README.md`, `.env.example`, `openspec/project.md`

**Sem breaking change na API pública:** `GET /api/images/{job_id}` e payload `images[]` nos turnos permanecem iguais.

## Impact

- Affected specs: `visual-assets` (MODIFIED), `web-interface` (sem alteração de contrato)
- Affected code: `backend/app/services/flux_client.py` (remover/substituir), `images.py`, `config.py`, `tests/test_images.py`, docs
- Supersedes parcialmente: decisões de `add-flux-visual-pipeline` (provider apenas; pipeline e UI intactos)
