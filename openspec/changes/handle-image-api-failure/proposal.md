# Proposal: handle-image-api-failure

**Data:** 2026-06-16  
**Status:** Draft  
**Escopo:** `backend/app/services/cloudflare_workers_ai.py` + `backend/app/services/images.py` + `frontend/src/components/session/SceneImage.tsx` + `frontend/src/hooks/useSessionPlay.ts`

---

## Problema

Quando a API de geração de imagens (Cloudflare Workers AI) está fora do ar, o comportamento atual **não é transparente** para o usuário — ao contrário do que deveria ser.

### Bugs identificados

#### Bug 1 — Placeholder visível quebra imersão

Em `images.py:130-133`:
```python
except (CloudflareNotConfigured, CloudflareGenerationError) as exc:
    job.status = "failed"
    job.image_url = placeholder_url(job.image_type)  # ← placeholder colorido do placehold.co
```

O `placeholder_url` gera URLs como `https://placehold.co/1024x576/1A1510/C9973A?text=Cena+WFRP`. O frontend exibe essa imagem no chat quando a API falha — um quadro colorido genérico que quebra a imersão narrativa.

#### Bug 2 — Erros de rede não são capturados → job preso em `"processing"`

`httpx.TimeoutException`, `httpx.ConnectError` e `httpx.HTTPStatusError` (4xx/5xx da CF) não herdam de `CloudflareGenerationError`. Quando a API está fora do ar e `httpx` lança essas exceções, elas escapam do `except (CloudflareNotConfigured, CloudflareGenerationError)` dentro de `process_image_job`. O `_run_image_job` captura via `except Exception` e loga, mas o job fica com `status="processing"` no banco para sempre. O frontend fica em loop de polling indefinidamente — spinner eterno.

#### Bug 3 — `SceneImage` renderiza mesmo com `status="failed"`

`SceneImage.tsx:53-54`:
```tsx
const displayUrl = job.image_url || job.placeholder_url;
```
Mesmo quando o job falha com `image_url = null`, o componente pode renderizar um `<figure>` vazio ou com placeholder.

---

## Solução proposta

### Princípio

> Imagem que falha = imagem que não existe. O chat deve continuar sem interrupção visual.

### Backend — `cloudflare_workers_ai.py` (generate_image)

**Envolver `httpx.HTTPStatusError` em `CloudflareGenerationError`** para que erros HTTP (incluindo 429 quota esgotada) sejam tipados e logáveis com contexto:

```python
try:
    response = await client.post(url, headers=headers, json=payload)
    response.raise_for_status()
except httpx.HTTPStatusError as exc:
    status = exc.response.status_code
    if status == 429:
        raise CloudflareGenerationError("Cloudflare quota/tokens esgotados (HTTP 429)") from exc
    raise CloudflareGenerationError(f"Cloudflare HTTP {status}") from exc
```

Isso cobre o caso de **tokens esgotados via HTTP 429** sem alterar a interface pública de `generate_image`. O JSON `success: false` com código de erro (quota via 200) já é tratado pelo `CloudflareGenerationError` existente.

### Backend — `images.py` (process_image_job)

**1. Capturar todos os erros:** Substituir `except (CloudflareNotConfigured, CloudflareGenerationError)` por `except Exception`, cobrindo também erros de rede não tipados (`httpx.ConnectError`, `httpx.TimeoutException`, etc.) que `cloudflare_workers_ai.py` não wrappa.

**2. Nunca usar placeholder em falha:** Em caso de qualquer erro, `status="failed"`, `image_url=None`. Sem URL de fallback.

**3. API não configurada:** Quando `client.enabled` é `False` (chaves CF ausentes), também `status="failed"`, `image_url=None`.

```python
try:
    if client.enabled:
        image_bytes = await client.generate_image(job.description, job.image_type)
        save_image_file(job_id, image_bytes)
        job.image_url = image_file_url(job_id)
        job.status = "completed"
    else:
        job.status = "failed"
        job.image_url = None
except Exception as exc:
    logger.warning("Image job %s failed (%s): %s", job_id, type(exc).__name__, exc)
    job.status = "failed"
    job.image_url = None
```

> Log de `WARNING` com `type(exc).__name__` — sem stack trace para falhas esperadas de rede. "quota/tokens esgotados" aparece explicitamente no log graças ao wrap em `cloudflare_workers_ai.py`.

### Cenários de falha cobertos

| Causa | Caminho | Capturado por |
|-------|---------|---------------|
| API fora do ar (503/502) | `raise_for_status` → `httpx.HTTPStatusError` → `CloudflareGenerationError` | `except Exception` em `process_image_job` |
| Tokens/quota esgotados (429) | `raise_for_status` → `httpx.HTTPStatusError` → `CloudflareGenerationError("quota...")` | `except Exception` em `process_image_job` |
| Quota via JSON (`success:false`) | `data.get("success", True)` → `CloudflareGenerationError` | `except Exception` em `process_image_job` |
| Timeout de rede | `httpx.TimeoutException` | `except Exception` em `process_image_job` |
| Sem conexão | `httpx.ConnectError` | `except Exception` em `process_image_job` |
| Chaves ausentes | `client.enabled == False` | `else` branch explícito |

### Frontend — `SceneImage.tsx`

Quando `status === "failed"`: retornar `null` — sem `<figure>`, sem spinner, sem placeholder. A entrada desaparece do chat silenciosamente.

```tsx
if (job.status === "failed") return null;
```

### Frontend — `useSessionPlay.ts` (appendImages)

Filtrar imagens que chegam com `status === "failed"` diretamente no `TurnResponse` — não adicionar à lista de `entries` se já falharam antes de chegar ao frontend.

```ts
const next = images
  .filter((img) => !existing.has(img.job_id) && img.status !== "failed")
  .map(...);
```

---

## O que NÃO muda

- Fluxo feliz (CF funcionando): sem alterações — imagens continuam sendo geradas e exibidas normalmente.
- `_link_job_assets`: já tem guarda `if job.status != "completed"` — não linka assets de jobs falhos.
- Polling no `SceneImage`: quando `status === "failed"`, o `useEffect` já para de pedir (condição `if (job.status === "completed" || job.status === "failed") return`).
- API pública `/images/{jobId}`: não alterada.

## Impacto narrativo

Quando a API está fora do ar, o GM continua narrando normalmente. A cena é descrita em texto. A ilustração simplesmente não aparece. O usuário não vê nenhuma mensagem de erro, nenhum placeholder quebrado, nenhum spinner eterno. A experiência é fluida.

---

## Sem breaking changes

- Resposta da API `/turn` inclui `images` — quando todos falharem, o array virá com `status="failed"` ou vazio.
- `ImageJobOut` já tem `image_url: str | None` — schema comporta `null`.
