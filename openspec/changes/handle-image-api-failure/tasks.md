# Tasks: handle-image-api-failure

## 1. Backend — cloudflare_workers_ai.py (generate_image)

- [x] 1.1 Envolver `response.raise_for_status()` em bloco `try/except httpx.HTTPStatusError` — detectar HTTP 429 e lançar `CloudflareGenerationError("Cloudflare quota/tokens esgotados (HTTP 429)")`, outros status como `CloudflareGenerationError(f"Cloudflare HTTP {status}")`
- [x] 1.2 (Opcional, sem alterar interface) Verificar se o JSON `success: false` já contém código de quota (ex.: `errors[].code == 10000`) e logar mensagem explícita `"quota esgotada"` — melhora diagnóstico sem alterar fluxo de exceção

## 2. Backend — process_image_job (images.py)

- [x] 2.1 Substituir `except (CloudflareNotConfigured, CloudflareGenerationError)` por `except Exception` para capturar `httpx.ConnectError`, `httpx.TimeoutException` e quaisquer outros erros não envolvidos
- [x] 2.2 Em caso de erro: `job.status = "failed"`, `job.image_url = None` (remover `placeholder_url`)
- [x] 2.3 Tratar `client.enabled == False` como falha silenciosa: `job.status = "failed"`, `job.image_url = None` (remover o `asyncio.sleep + placeholder_url` do else)
- [x] 2.4 Log: `logger.warning("Image job %s failed (%s): %s", job_id, type(exc).__name__, exc)` — sem stack trace

## 3. Frontend — SceneImage.tsx

- [x] 3.1 Adicionar guarda no início do componente: `if (job.status === "failed") return null`
- [x] 3.2 Confirmar que o `useEffect` de polling já para quando `status === "failed"` (condição na linha 28 — apenas verificar, sem alteração)

## 4. Frontend — useSessionPlay.ts (appendImages)

- [x] 4.1 Filtrar `img.status !== "failed"` no `images.filter(...)` de `appendImages` para não adicionar entradas de imagem já falhas à lista de `entries`

## 5. Validação

- [ ] 5.1 **Tokens/quota esgotados:** usar token CF inválido (simula 401/403) → confirmar que job fica `"failed"` no banco e log exibe `CloudflareGenerationError` com status HTTP
- [ ] 5.2 **API fora do ar:** desconfigurar `CLOUDFLARE_ACCOUNT_ID` → enviar turno com `[IMAGEM]` → confirmar que nenhum spinner ou placeholder aparece no chat
- [ ] 5.3 **429 explícito:** mockar resposta 429 em teste unitário → confirmar que `CloudflareGenerationError("quota/tokens esgotados")` é lançado e job fica `"failed"`
- [ ] 5.4 **Timeout:** reducir `httpx` timeout para 0.001s em test → confirmar que `httpx.TimeoutException` é capturado por `except Exception` e job fica `"failed"` (não `"processing"`)
- [ ] 5.5 **Fluxo feliz (regressão):** com CF configurada, confirmar que imagens continuam sendo geradas e exibidas normalmente
- [ ] 5.6 `npm run build` — zero erros TypeScript ✓
- [ ] 5.7 `ruff check backend/app/services/images.py backend/app/services/cloudflare_workers_ai.py` — zero erros ✓
