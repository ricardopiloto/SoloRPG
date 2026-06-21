# Proposal: session-image-credits-guard

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `handle-image-api-failure` (falha silenciosa de jobs individuais)

---

## Why

A geração de imagens consome créditos da API Cloudflare Workers AI com quota limitada. Hoje, cada sinal `[IMAGEM]` do GM dispara um job independente — mesmo quando a quota já está esgotada, o sistema continua enfileirando tentativas que falham silenciosamente turno a turno, desperdiçando latência e poluindo logs. Precisamos detectar indisponibilidade de créditos cedo (início da sessão) e cortar novas tentativas assim que a quota acabar no meio do jogo.

## What Changes

- **Probe de créditos no início da sessão:** ao criar uma sessão nova, o backend envia uma requisição real de geração de imagem (prompt mínimo de validação) à Cloudflare. Se falhar, a sessão fica marcada como sem imagens pelo resto da sessão.
- **Flag de sessão `images_enabled`:** novo campo em `GameSession` persiste se a sessão pode gerar imagens. Inicia `true` após probe bem-sucedido; vira `false` em falha no probe ou em falha de quota mid-session.
- **Guard no pipeline de imagens:** `_handle_signal` para `[IMAGEM]` ignora o sinal quando `images_enabled=false` — nenhum `ImageJob` é criado, nenhum spinner aparece.
- **Desligamento mid-session:** quando um job falha por quota/créditos esgotados (HTTP 429, código 10000, ou erro tipado equivalente), `images_enabled` passa a `false` para aquela sessão; jobs subsequentes não são enfileirados.
- **Retomada de sessão pausada:** sessões retomadas reutilizam o flag já persistido — não re-probe (evita consumir crédito extra e respeita estado anterior).
- **Transparência ao jogador:** sem mensagens de erro; narrativa continua normalmente, apenas sem ilustrações.
- **API:** `SessionOut` e `SessionDetailOut` expõem `images_enabled: boolean`.

## Capabilities

### New Capabilities

- `session-image-credits-guard`: Validação de créditos no início da sessão via probe real e desligamento automático mid-session quando quota esgota.

### Modified Capabilities

- `visual-assets`: Comportamento de geração de imagens passa a respeitar flag de sessão antes de enfileirar jobs.

## Impact

| Área | Alterações |
|------|------------|
| Backend | `GameSession` + migration Alembic, `session.py`, `probe_image_credits`, `images.py`, `gm_orchestrator.py`, `cloudflare_workers_ai.py` |
| API | `SessionOut` / `SessionDetailOut` expõem `images_enabled` |
| Frontend | Nenhuma mudança obrigatória |
| Infra | 1 crédito de imagem por sessão nova (custo do probe) |
