# Tasks: session-image-credits-guard

## 1. Modelo e migration

- [x] 1.1 Adicionar coluna `images_enabled` (Boolean, default `false`) em `GameSession` (`backend/app/db/models.py`)
- [x] 1.2 Criar migration Alembic para `images_enabled` em `game_sessions`

## 2. Cloudflare — classificação e probe

- [x] 2.1 Implementar `is_quota_or_credit_error(exc)` em `cloudflare_workers_ai.py` (429, code 10000, `CloudflareNotConfigured`, mensagem quota)
- [x] 2.2 Implementar `probe_image_credits()` com prompt fixo `"minimal dark fantasy landscape, validation probe"` (tipo `"cena"`) — descartar bytes gerados
- [x] 2.3 Probe com credenciais ausentes SHALL falhar localmente sem HTTP

## 3. Sessão — probe no start

- [x] 3.1 Chamar probe síncrono em `start_session()` após criar `GameSession` nova
- [x] 3.2 Probe ok → persistir `images_enabled = true`; falha → `false`
- [x] 3.3 Sessão pausada retomada → reutilizar flag existente, sem re-probe

## 4. Pipeline de imagens — guard e desligamento

- [x] 4.1 Guard em `_handle_signal` (`gm_orchestrator.py`): ignorar `[IMAGEM]` quando `images_enabled=false`
- [x] 4.2 Em `process_image_job` (`images.py`): quota mid-session → `session.images_enabled = false`
- [x] 4.3 Erros transitórios (503, timeout) NÃO alteram `images_enabled`

## 5. API

- [x] 5.1 Expor `images_enabled: boolean` em `SessionOut` e `SessionDetailOut` (`schemas/api.py` + rotas)

## 6. Testes automatizados

- [x] 6.1 Teste: probe ok habilita imagens
- [x] 6.2 Teste: probe falho desabilita imagens
- [x] 6.3 Teste: sessão retomada não re-probe
- [x] 6.4 Teste: guard ignora `[IMAGEM]` quando desabilitado
- [x] 6.5 Teste: quota mid-session desliga sessão
- [x] 6.6 Teste: erro transitório não desliga sessão

## 7. Validação manual

- [ ] 7.1 Sessão com CF válido → probe ok e imagens no turno
- [ ] 7.2 CF inválido → zero spinners/imagens na sessão
- [ ] 7.3 Quota esgotada mid-session → imagens param após primeira falha de quota
