# Design: session-image-credits-guard

## Context

O pipeline de imagens usa Cloudflare Workers AI com quota limitada. Cada sinal `[IMAGEM]` do GM enfileira um `ImageJob` independente. Mesmo com quota esgotada, jobs continuam sendo criados e falham silenciosamente (`handle-image-api-failure`), gerando latência desnecessária e logs repetidos.

Estado atual: falhas individuais de job são tratadas sem UI; não há detecção proativa de créditos nem flag de sessão.

## Goals / Non-Goals

**Goals:**

- Detectar indisponibilidade de créditos no início de sessões novas via probe real.
- Persistir `images_enabled` em `GameSession` para cortar novos jobs quando desabilitado.
- Desligar imagens mid-session apenas em erros de quota/crédito (não em falhas transitórias).
- Reutilizar flag em sessões pausadas retomadas (sem re-probe).
- Expor `images_enabled` na API de sessão.

**Non-Goals:**

- Mensagens de erro ou aviso ao jogador.
- Alterações obrigatórias no frontend.
- Re-probe automático após quota restaurada mid-session.
- Billing ou dashboard de consumo de créditos.

## Decisions

### 1. Flag `images_enabled` em `GameSession`

**Decisão:** Coluna booleana `images_enabled` (default `false` até probe confirmar).

**Alternativa rejeitada:** Cache em memória por sessão — perdido em restart e retomada de sessão pausada.

### 2. Probe síncrono em `start_session`

**Decisão:** Após criar `GameSession` nova, chamar `probe_image_credits()` com prompt fixo `"minimal dark fantasy landscape, validation probe"` (tipo `"cena"`). Bytes descartados.

| Evento | `images_enabled` |
|--------|-------------------|
| Sessão nova criada | `False` → probe → `True` se sucesso |
| Probe falha (qualquer motivo) | permanece `False` |
| Sessão pausada retornada | valor existente, sem probe |
| Job falha por quota mid-session | `False` |
| Erro transitório (503, timeout) | inalterado |

**Alternativa rejeitada:** Probe assíncrono — primeiro turno poderia enfileirar imagem antes do resultado.

### 3. Classificação de erro de quota

Função `is_quota_or_credit_error()` em `cloudflare_workers_ai.py`:

| Condição | Conta como quota? |
|----------|-------------------|
| `CloudflareNotConfigured` | Sim |
| HTTP 429 / mensagem `"quota/tokens esgotados"` | Sim |
| JSON error code `10000` | Sim |
| Timeout, ConnectError, HTTP 503 | Não |

**Probe:** qualquer falha → `images_enabled = false`  
**Mid-session:** só erros de quota desligam a sessão inteira

### 4. Guard em `_handle_signal`

Quando `images_enabled=false`, sinal `[IMAGEM]` é ignorado silenciosamente — sem `ImageJob`, sem placeholder, sem spinner.

Cache hit continua funcionando quando `images_enabled=true`.

### 5. Desligamento em `process_image_job`

Após falha de quota em job mid-session, persistir `session.images_enabled = false`. Jobs já enfileirados podem completar; novos não são criados após desligamento.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Probe consome 1 crédito por sessão nova | Custo aceito vs. múltiplas falhas silenciosas por sessão |
| Probe falha por timeout transitório desliga imagens na sessão | Probe trata qualquer falha como indisponível — sessão continua sem imagens |
| Quota restaurada mid-session não reativa imagens | Comportamento documentado; jogador não vê erro |
| Sessões pausadas com flag stale | Respeita estado anterior — evita crédito extra e inconsistência |

## Migration Plan

1. Alembic migration adiciona `images_enabled` em `game_sessions` (default `false`).
2. Deploy backend — sessões existentes retomadas mantêm valor migrado (`false` até probe em novas sessões).
3. Rollback: remover guard e probe; coluna pode permanecer sem efeito.

## Open Questions

Nenhuma — comportamento definido no export de propostas.
