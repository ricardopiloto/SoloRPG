# Proposal: switch-to-openrouter-images

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `switch-to-cloudflare-workers-ai` (archived), `session-image-credits-guard`, `handle-image-api-failure`

---

## Why

A geração de ilustrações usa hoje **Cloudflare Workers AI** (`flux-1-schnell`) com duas variáveis de ambiente (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`) e endpoint proprietário da CF. O projeto já centraliza integrações externas em adapters; OpenRouter oferece uma **Image API unificada** (`POST /api/v1/images`) com modelo **FLUX.2 Klein 4B** — mais rápido, pay-per-megapixel, e uma única chave `OPENROUTER_API_KEY`.

Migrar reduz acoplamento ao ecossistema Cloudflare (túnel ≠ Workers AI) e alinha com o snippet de referência fornecido pelo usuário.

---

## What Changes

### 1. Novo cliente OpenRouter (`openrouter_images.py`)

Substituir `cloudflare_workers_ai.py` por módulo equivalente:

| Função / tipo | Comportamento preservado |
|---------------|-------------------------|
| `OpenRouterImagesClient` | `enabled`, `generate_image(description, image_type)` → `bytes` |
| `OpenRouterNotConfigured` | Chave ausente |
| `OpenRouterGenerationError` | Erros HTTP, JSON inválido, resposta sem imagem |
| `probe_image_credits()` | Probe no início de sessão (prompt fixo, bytes descartados) |
| `is_quota_or_credit_error()` | HTTP 402/429, mensagens quota/credits |
| `WFRP_STYLE_PREFIX`, `COMPOSITION_HINTS` | Mesmos prefixos de prompt WFRP |

**Chamada API:**

```http
POST https://openrouter.ai/api/v1/images
Authorization: Bearer {OPENROUTER_API_KEY}
Content-Type: application/json

{
  "model": "black-forest-labs/flux.2-klein-4b",
  "prompt": "<WFRP prefix + hint + description>",
  "output_format": "jpeg",
  "aspect_ratio": "16:9"
}
```

**Resposta:** decodificar `data[0].b64_json` → bytes salvos como `.jpg` (pipeline existente).

### 2. Configuração

| Remover | Adicionar |
|---------|-----------|
| `CLOUDFLARE_ACCOUNT_ID` | `OPENROUTER_API_KEY` |
| `CLOUDFLARE_API_TOKEN` | `OPENROUTER_IMAGE_MODEL` (default: `black-forest-labs/flux.2-klein-4b`) |
| `CLOUDFLARE_AI_MODEL` | — |

Atualizar: `config.py`, `.env.example`, `.env.docker.example`, `Docs/debian-server-install.md`, `Docs/architecture.md`, `openspec/project.md`.

### 3. Pipeline inalterado (escopo preservado)

- Fila assíncrona (`queue_image`, `process_image_job`)
- Cache por `build_cache_key`
- Guard de sessão (`images_enabled`, probe, desligamento por quota)
- Placeholders temáticos **somente** enquanto job `pending`/`processing` (não em falha — alinhado a `handle-image-api-failure`)
- Frontend (`SceneImage`, polling) **sem mudança de contrato**

### 4. Testes

- Renomear/adaptar `test_images.py` e `test_session_image_credits_guard.py`
- Mock `httpx` com resposta OpenRouter `{ "data": [{ "b64_json": "..." }] }`
- Cenários: sucesso, chave ausente, HTTP 402 quota, resposta vazia

### 5. Spec deltas

- `visual-assets`: provider OpenRouter + modelo Klein 4B
- `session-image-credits-guard`: probe/credenciais via `OPENROUTER_API_KEY`

---

## Out of Scope

- Trocar o LLM narrativo para OpenRouter (DeepSeek permanece)
- Streaming SSE de imagens parciais
- `input_references` / image-to-image
- Suporte dual Cloudflare + OpenRouter (cutover único)
- Alterar tipos de imagem (`cena`, `personagem`, `mapa`, `item`) ou protocolo `[IMAGEM]`

---

## Acceptance Criteria

1. Com `OPENROUTER_API_KEY` válida, turno com `[IMAGEM]` gera ilustração via Klein 4B e exibe no chat.
2. Sem chave, probe falha localmente → `images_enabled=false`, sem jobs enfileirados.
3. HTTP 402/429 desliga `images_enabled` mid-session (comportamento IMG-CRED-03 preservado).
4. Variáveis `CLOUDFLARE_*` removidas do código e exemplos de env.
5. `pytest backend/tests/test_images.py backend/tests/test_session_image_credits_guard.py` passa.
6. `openspec validate switch-to-openrouter-images --strict` passa.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| Deploys com `CLOUDFLARE_*` antigas param de gerar imagens | Documentar migração em CHANGELOG + debian-server-install |
| Klein 4B retorna PNG apesar de `output_format: jpeg` | Aceitar bytes como estão; salvar `.jpg` ou detectar magic bytes (implementação) |
| Custo por megapixel vs. quota CF | Probe no início de sessão continua validando créditos reais |
| `handle-image-api-failure` draft paralelo | Implementação MUST manter `image_url=None` em falha; não reintroduzir placeholder em erro |
