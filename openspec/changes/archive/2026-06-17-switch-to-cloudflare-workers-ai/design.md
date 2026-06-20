## Context

O pipeline de imagens já implementado em `add-flux-visual-pipeline`:

```
[IMAGEM] → queue_image() → ImageJob (pending)
         → background task → FluxClient → image_url
         → GET /api/images/{id} ← SceneImage (polling frontend)
```

A troca afeta **apenas o provider HTTP** e **como a URL final é materializada**. O frontend (`SceneImage`, `ChatLog`, inventário, mapa) não precisa mudar contrato.

Documentação de referência:
- `Docs/session-flow.md` §7 — fluxo assíncrono com Cloudflare
- `Docs/technical-research.md` §6 — FLUX.1 Schnell via Workers AI
- [Cloudflare Workers AI — flux-1-schnell](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/)

## Goals / Non-Goals

**Goals:**
- Gerar imagens via `POST /client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell`
- Manter geração assíncrona no backend (não bloquear narrativa)
- URLs estáveis servidas pelo backend (não data URIs gigantes no SQLite)
- Fallback para placeholder temático quando credenciais ausentes
- Cache semântico por `cache_key` preservado

**Non-Goals:**
- WebSocket/SSE para push de imagens (polling existente é suficiente)
- Suporte multi-provider (BFL + Cloudflare em paralelo)
- Upload para Supabase Storage / CDN externo (fase futura)
- Trocar modelo para SDXL ou outros do catálogo Cloudflare

## Decisions

### 1. Cliente HTTP dedicado

Criar `cloudflare_workers_ai.py` com:
- Endpoint: `https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell`
- Auth: `Authorization: Bearer {CLOUDFLARE_API_TOKEN}`
- Body: `{ "prompt": "...", "steps": 4 }` (steps 1–8, default 4)
- Resposta: `{ "result": { "image": "<base64>" } }` (validar formato exato na implementação)

Remover `flux_client.py` após migração.

### 2. Persistência de imagens (base64 → arquivo)

**Problema:** BFL retornava URL assinada (expira ~10 min). Cloudflare retorna base64 inline.

**Decisão:** Salvar JPEG em disco e expor via rota estática do FastAPI.

```
backend/generated_images/{job_id}.jpg
image_url = {API_BASE}/api/images/{job_id}/file
```

| Abordagem | Prós | Contras |
|-----------|------|---------|
| Data URI no DB | Zero infra | Infla SQLite; cache duplicado |
| Arquivo local + rota | URL estável; DB leve | Disco local (ok para MVP) |
| Supabase Storage | Produção-ready | Escopo extra |

Para MVP pessoal: **arquivo local**. Documentar limpeza opcional por idade.

### 3. Prompt e dimensões

Manter prefixo WFRP existente em `images.py`:
```
"Dark fantasy illustration, Warhammer Fantasy Roleplay style, ..."
```

`flux-1-schnell` não aceita `width`/`height` na API REST documentada — usar prompt enriquecido com composição quando necessário (ex.: "wide landscape scene" para mapas). Não simular dimensões via parâmetros inexistentes.

### 4. Pipeline de jobs inalterado

| Status | Comportamento |
|--------|---------------|
| `pending` | Job criado; placeholder temático |
| `processing` | Chamada Cloudflare em background |
| `completed` | Arquivo salvo; `image_url` atualizada; vínculos mapa/item |
| `failed` | Placeholder mantido; log de erro |

Cloudflare é **síncrono por request**, mas nosso **job continua assíncrono** via `asyncio.create_task` — narrativa não bloqueia.

### 5. Configuração

```env
# Remover
FLUX_API_KEY=
FLUX_API_URL=

# Adicionar
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
# Opcional: modelo override (default flux-1-schnell)
CLOUDFLARE_AI_MODEL=@cf/black-forest-labs/flux-1-schnell
```

Sem credenciais → mesmo fallback atual (placeholder WFRP, status `completed`).

### 6. Testes

- Mock `httpx` POST para Cloudflare API
- Verificar gravação de arquivo e URL servida
- Manter testes de cache, map region, item linking
- Remover testes específicos de polling BFL

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Qualidade Schnell < Flux 1.1 Pro | Aceitável para MVP; prompt WFRP compensa; modelo trocável via env |
| Cota Cloudflare (neurons) | Log de uso; fallback placeholder; documentar limites no README |
| Disco local cresce | `.gitignore` em `generated_images/`; script de limpeza futuro |
| Base64 grande em memória | Stream decode; timeout 30s na request |

## Migration Plan

1. Implementar `CloudflareWorkersAIClient` + rota `/api/images/{id}/file`
2. Trocar `images.py` para usar novo client
3. Atualizar testes e `.env.example`
4. Remover `flux_client.py` e vars `FLUX_*`
5. Atualizar docs (`product-brief`, `README`, `project.md`, `frontend-backend-split`)
6. Validar manualmente com `CLOUDFLARE_*` reais

**Rollback:** Reverter commit; restaurar `flux_client.py` e vars BFL.

## Open Questions

- **Limpeza de arquivos:** política de retenção (ex.: 30 dias) — implementar agora ou adiar?
- **Produção (Railway/Fly):** volume efêmero pode perder imagens no redeploy — aceitar para MVP ou planejar Supabase Storage na Fase 6?
