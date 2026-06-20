## Context

O sistema atual de timer é wall-clock puro: `time_remaining = duration_minutes - elapsed_since_started_at`. Se o jogador fecha o navegador, o timer segue correndo. Não há conceito de "sessão pausada" — a sessão permanece `is_active=True` até `[FIM_SESSAO]` ou um encerramento forçado via API.

O histórico de chat também não é restaurável: a frontend monta `entries` acumulando os eventos recebidos via streaming durante a sessão atual. Ao recarregar a página (mesmo dentro da sessão), o chat fica vazio.

## Goals / Non-Goals

- **Goals:**
  - Congelar o timer no momento da pausa; retomá-lo de onde parou
  - Restaurar o histórico completo de chat ao retomar uma sessão pausada
  - Impedir que o jogador crie uma segunda sessão enquanto há uma pausada
  - Fluxo simples: "Pausar" → navegar → "Retomar"

- **Non-Goals:**
  - Auto-save automático por inatividade (a sessão já persiste no banco; só o timer e o histórico de exibição precisam ser resolvidos)
  - Múltiplas sessões pausadas simultâneas para a mesma campanha
  - Suporte a pausa durante fase de combate com estados intermediários complexos — a pausa durante combate é permitida, mas o estado de combate (`combat_state`) já persiste no modelo
  - Checkpoint incremental a cada turno (o `turn_history` já é persistido a cada `append_turn`)

## Decisions

### Timer: campo `total_paused_seconds` (abordagem aditiva)

Em vez de recalcular `started_at` ao resumir (o que perde a informação de quando a sessão começou de fato), mantemos `started_at` imutável e somamos a duração total das pausas.

```
time_remaining = duration_minutes * 60
                 - (now - started_at).total_seconds()
                 + total_paused_seconds
```

Quando a sessão é pausada, registramos `paused_at = now`. Quando resumida, adicionamos `(now - paused_at).seconds` a `total_paused_seconds` e zeramos `paused_at`.

**Alternativas descartadas:**
- Ajustar `started_at` para frente ao resumir → perde o timestamp real de início, mais difícil de auditar
- Armazenar `remaining_minutes` como snapshot → perde precisão (segundos descartados)

### Restauração do histórico de chat: endpoint `GET /sessions/{id}/history`

Os `SessionTurn` já estão persistidos. Criamos um endpoint que retorna todos os turnos de uma sessão em ordem cronológica, com `role` e `content`, para o frontend reconstruir `entries`.

O frontend mapeia:
- `role="user"` → `{ kind: "player", content }`
- `role="assistant"` → `{ kind: "narrative", content }`
- `role="system"` com `metadata.quick_roll` → `{ kind: "roll", content, success }`

Imagens (`role="system"` com `metadata.images`) são re-emitidas como `{ kind: "image" }` com `jobId`, mas o status precisa ser recarregado via polling — comportamento já existente.

**Alternativas descartadas:**
- Guardar `entries` no localStorage → dados sensíveis de narrativa no cliente; conflito entre abas; sem compressão
- Recriar apenas o último turno → perda de contexto visual para o jogador

### `start_session` retorna sessão pausada existente

Se o jogador clica "Iniciar sessão" mas já há uma sessão `is_active=True AND paused_at IS NOT NULL`, o backend retorna a sessão pausada com HTTP 200 (não cria nova). O campo `paused_at` indica ao frontend que deve chamar `POST /resume` antes de interagir.

### Pausa durante `awaiting_roll`

Se `turn_phase == "awaiting_roll"`, a pausa é permitida — o `pending_test` persiste no banco. Ao retomar, o frontend recarrega `turn_phase` e `pending_test` e reexibe o bloco de teste.

## Risks / Trade-offs

- **Turn history grande**: sessões longas podem ter muitos `SessionTurn`. O endpoint de histórico usa `selectinload` e pagina retornando todos — aceitável para MVPs com sessões de até 2h (~200 turnos máx).
- **Pausa enquanto streaming**: se o jogador pausar no meio de um streaming de narrativa, o token parcial pode não ter sido persistido. Mitigação: desabilitar o botão "Pausar" durante `loading=true`.
- **Migração de schema**: `ALTER TABLE game_sessions ADD COLUMN paused_at TIMESTAMPTZ, ADD COLUMN total_paused_seconds INT DEFAULT 0` — não-breaking, colunas nullable/com default.

## Migration Plan

1. Adicionar colunas ao modelo SQLAlchemy
2. Script de migração Alembic (ou `create_all` em dev com SQLite — tabela recriada)
3. Implementar service functions e endpoints
4. Implementar frontend
5. Atualizar E2E: testar fluxo pausa → retomada

## Open Questions

- Após quanto tempo uma sessão pausada expira automaticamente? Proposta: nunca expira automaticamente (o jogador decide quando encerrar definitivamente via `[FIM_SESSAO]`). Um cron de limpeza pode ser adicionado depois.
- O timer deve aparecer congelado na tela de `/campaigns` mostrando o tempo restante ao pausar? Proposta: sim, exibir "X min restantes" no card da sessão pausada.
