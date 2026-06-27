# Design: switch-to-openrouter-images

## Contexto

```
GM [IMAGEM] → signals.py → images.queue_image()
                              ↓
                    process_image_job (async)
                              ↓
              CloudflareWorkersAIClient  ←── substituir
                              ↓
                    save generated_images/{id}.jpg
                              ↓
                    GET /api/images/{id}/file → SceneImage
```

O pipeline assíncrono, cache SHA256, prioridade `marco`, e guard `images_enabled` **não mudam**. Apenas o **provider HTTP** e **config** mudam.

Referência histórica: change arquivada `2026-06-17-switch-to-cloudflare-workers-ai`.

---

## API OpenRouter Image

Documentação: [OpenRouter Image Generation](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)

| Campo | Valor | Motivo |
|-------|-------|--------|
| Endpoint | `https://openrouter.ai/api/v1/images` | Unified Image API |
| Auth | `Authorization: Bearer {OPENROUTER_API_KEY}` | Uma chave |
| `model` | `black-forest-labs/flux.2-klein-4b` | Escolha do usuário; default em config |
| `prompt` | Prefixo WFRP existente + hint por tipo | Paridade visual com CF |
| `output_format` | `jpeg` | Alinha com `.jpg` em disco |
| `aspect_ratio` | `16:9` | Paridade com placeholder 1024×576 |

Headers opcionais (rankings OpenRouter, não obrigatórios):

- `HTTP-Referer`: URL do app (ex. `API_BASE_URL`)
- `X-Title`: `WFRP Solo`

### Resposta de sucesso

```json
{
  "data": [
    { "b64_json": "<base64>" }
  ],
  "usage": { ... }
}
```

Decodificar `data[0].b64_json`. Se `data` vazio → `OpenRouterGenerationError`.

### Erros e mapeamento para quota

| Condição | Exceção | `is_quota_or_credit_error` |
|----------|---------|---------------------------|
| Chave ausente | `OpenRouterNotConfigured` | sim |
| HTTP 402 Payment Required | `OpenRouterGenerationError` | sim |
| HTTP 429 | `OpenRouterGenerationError` | sim |
| HTTP 401 | `OpenRouterGenerationError` | não (credencial inválida — probe falha, não desliga mid-session por quota*) |
| Timeout / ConnectError | propagar ou wrap | não |
| HTTP 503 | wrap | não |

\*401 no probe → `images_enabled=false` na criação; em job mid-session tratar como falha individual (IMG-CRED-03 transitório).

Mensagens JSON com `"quota"`, `"credit"`, `"insufficient"` no body → quota.

---

## Módulo `openrouter_images.py`

Estrutura espelhando `cloudflare_workers_ai.py`:

```python
class OpenRouterImagesClient:
    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def generate_image(self, description: str, image_type: str = "cena") -> bytes:
        ...
```

Constantes movidas intactas: `WFRP_STYLE_PREFIX`, `COMPOSITION_HINTS`, `PROBE_PROMPT`, `PROBE_IMAGE_TYPE`.

`probe_image_credits(client=None) -> bool` — mesma semântica.

---

## Alterações por arquivo

| Arquivo | Mudança |
|---------|---------|
| `backend/app/services/openrouter_images.py` | **Novo** — cliente + helpers |
| `backend/app/services/cloudflare_workers_ai.py` | **Remover** |
| `backend/app/services/images.py` | Import `OpenRouterImagesClient` |
| `backend/app/services/session.py` | Import `probe_image_credits` do novo módulo |
| `backend/app/config.py` | `openrouter_api_key`, `openrouter_image_model` |
| `backend/tests/test_images.py` | Mocks OpenRouter |
| `backend/tests/test_session_image_credits_guard.py` | Env `OPENROUTER_API_KEY` |
| `.env.example`, `.env.docker.example` | Vars OpenRouter |
| `Docs/architecture.md`, `Docs/debian-server-install.md` | Tabela deps + troubleshooting |
| `openspec/project.md` | Tech stack + External Dependencies |
| `CHANGELOG.md` | Entrada Unreleased |

**Frontend:** nenhuma alteração (contrato REST inalterado).

---

## Prompt building (paridade)

Manter lógica existente:

```python
WFRP_STYLE_PREFIX = (
    "Dark fantasy illustration, Warhammer Fantasy Roleplay style, "
    "grim medieval atmosphere, muted palette, painterly: "
)
COMPOSITION_HINTS = {
    "cena": "wide cinematic scene, ",
    "personagem": "character portrait, ",
    "mapa": "wide landscape map view, fantasy cartography, ",
    "item": "isolated item on dark background, ",
}
```

OpenRouter não exige `steps` (CF usava `steps: 4`); Klein 4B é otimizado para throughput — prompt + aspect ratio bastam.

---

## Migração de deploy

1. Criar/obter chave em [openrouter.ai/keys](https://openrouter.ai/keys)
2. Definir `OPENROUTER_API_KEY` no `backend/.env`
3. Remover `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_AI_MODEL`
4. Reiniciar backend; nova sessão executa probe Klein 4B

**Nota:** Cloudflare Tunnel (roteamento HTTPS em `debian-server-install.md`) permanece válido — é infra de rede, não provider de imagem.

---

## Relação com `handle-image-api-failure`

Change draft `handle-image-api-failure` propõe melhorias de UX em falha (sem placeholder colorido, captura ampla de exceções). `images.py` **já** implementa parte disso (`image_url=None` em falha). Esta migração MUST:

- Preservar `except Exception` em `process_image_job`
- Não reintroduzir `placeholder_url` em jobs `failed`
- Envolver `httpx.HTTPStatusError` no novo cliente (como CF já faz)

Implementar ambos na mesma PR ou sequência: primeiro OpenRouter, depois fechar tasks restantes de `handle-image-api-failure` se ainda pendentes.

---

## Decisões descartadas

| Alternativa | Motivo de rejeição |
|-------------|-------------------|
| Abstração multi-provider (CF + OR) | YAGNI — usuário pediu cutover OpenRouter |
| Reutilizar endpoint chat `/chat/completions` com modalities | Image API dedicada é documentada e retorna `b64_json` direto |
| Modelo `flux.2-pro` | Usuário especificou `flux.2-klein-4b` (custo/latência) |
