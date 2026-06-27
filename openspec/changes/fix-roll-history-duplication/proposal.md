# Proposal: fix-roll-history-duplication

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `add-game-chat-ux`, `update-gm-prompt-perception`, `defer-gm-narrative-presentation`

---

## Why

A aba **Rolagens** na `DiarySidebar` exibe entradas duplicadas: o jogador realizou 2 testes de Percepção na sessão e vê **4 entradas idênticas** (cada rolagem aparece duas vezes).

Causa raiz (frontend): cada teste solicitado pelo GM passa por dois handlers que **acumulam o mesmo `roll_results`**:

1. `POST /roll` → `applyRollResponse()` → `appendRolls(res.roll_results)`
2. `POST /roll/narrate/stream` → `applyMeta(finalResult)` → `appendRolls(result.roll_results)` — payload `done` reenvia os mesmos rolls de `pending_roll_result`

O backend ecoa `roll_results` na narração pós-teste **de propósito** (metadado do turno GM persistido em `metadata.rolls`); o bug é **dupla ingestão no cliente**, não dupla persistência no servidor.

Gap secundário: ao recarregar a sessão, `rollHistory` inicia vazio — o chat restaura via `GET /history`, mas rolagens **não** são reconstruídas de `metadata.rolls`.

---

## What Changes

### 1. Frontend — ingestão única por rolagem

- Remover `appendRolls` de `applyMeta()` **ou** condicionar para não re-adicionar rolls já registrados no fluxo `roll → narrate`.
- Manter registro em:
  - `applyRollResponse()` — testes GM e re-roll Fortuna
  - `handleDiceRollComplete()` (quick-roll espontâneo) — já separado
- Fluxo `runStreamTurn` / `applyMeta` continua atualizando mood, imagens, fase, ferimentos — sem duplicar histórico.

### 2. Frontend — restaurar histórico ao carregar sessão

- Em `useSessionPlay.load()`, reconstruir `rollHistory` a partir de `GET /sessions/{id}/history`:
  - `role=gm` + `metadata.rolls[]`
  - `role=system` + `metadata.quick_roll`
- Ordem cronológica; contagem = número real de rolagens persistidas.

### 3. Testes

- Teste unitário extraído (ex.: `buildRollHistoryFromTurns`) ou teste de hook: 1 roll + 1 narrate → **1** entrada.
- Opcional: teste de reconstrução a partir de turns mock.

### 4. Spec delta

- `session-ui`: MODIFIED `Histórico de rolagens` — proibir duplicatas; exigir restauração ao carregar sessão.

---

## Out of Scope

- Alterar payload SSE `done.roll_results` no backend (consumidores futuros podem usar; frontend deixa de duplicar).
- Deduplicação por heurística roll+target+timestamp (correção na fonte, não band-aid).
- Paginação ou persistência separada de roll log (já em `SessionTurn.metadata`).

---

## Acceptance Criteria

1. Dois testes GM na mesma sessão → aba Rolagens mostra **2** entradas, não 4.
2. Re-roll Fortuna → substitui/adiciona conforme design (1 entrada por resolução mecânica final, sem eco do narrate).
3. Recarregar `/play/{sessionId}` → Rolagens restauradas do histórico persistido.
4. Quick-roll espontâneo continua com 1 entrada + flag `spontaneous`.
5. `openspec validate fix-roll-history-duplication --strict` passa.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| Remover append de applyMeta quebra fluxo sem applyRollResponse | Auditar callers; GM tests sempre passam por applyRollResponse |
| Rebuild from history duplica se somar client + server | Ao carregar, **substituir** rollHistory, não append sobre estado local |
| React Strict Mode double-mount | `historyLoadedRef` + setRollHistory from turns once |
