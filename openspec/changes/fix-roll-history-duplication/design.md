# Design: fix-roll-history-duplication

## Fluxo atual (bug)

```
Jogador rola teste GM
        │
        ▼
POST /sessions/{id}/roll
        │
        ▼
applyRollResponse()
        │
        └── appendRolls([Percepção 42 vs 35])  ──► rollHistory: [A]
        │
        ▼
POST /sessions/{id}/roll/narrate/stream
        │
        ▼
applyMeta(done)
        │
        └── appendRolls([Percepção 42 vs 35])  ──► rollHistory: [A, A]  ← DUPLICATA
```

Mesmo `roll_results` vem de `session.pending_roll_result` no backend (`stream_narrate_roll`, linha ~337).

Quick-roll **não** duplica — só `setRollHistory` em `handleDiceRollComplete`, e `applyMeta` não roda no mesmo fluxo.

---

## Correção proposta

### Opção escolhida: rolls fora de `applyMeta`

`applyMeta()` SHALL NOT chamar `appendRolls()`.

Responsabilidade de histórico:

| Origem | Onde registrar |
|--------|----------------|
| Teste GM (`/roll`) | `applyRollResponse` |
| Fortuna re-roll | `applyRollResponse` |
| Quick-roll sidebar | `handleDiceRollComplete` |

`applyMeta` mantém: `scene_mood`, `images`, `session` state, `pendingTest`, diary/NPC refresh, wounds refresh.

**Justificativa:** `TurnResponse.roll_results` em eventos `done` de **narração** é eco do turno mecânico anterior, não nova rolagem. Em `process_turn`/`stream_turn` normal, `roll_results` já vem vazio.

Alternativa rejeitada: dedupe por `(roll, target, label)` — mascara bugs futuros e falha em re-rolls legítimos com mesmo alvo.

---

## Restauração ao carregar sessão

Hoje `load()`:

```typescript
const turns = await api.getSessionHistory(sessionId);
setEntries(turnsToEntries(turns));
// rollHistory permanece []
```

Proposta — função `buildRollHistoryFromTurns(turns: SessionTurnOut[])`:

```typescript
for (const turn of turns) {
  if (turn.role === "gm" && meta.rolls) → append each roll
  if (turn.role === "system" && meta.quick_roll) → append spontaneous roll
}
setRollHistory(entries); // replace, not append
```

Backend já persiste:

```python
await append_turn(db, session, "gm", result.narrative, {"rolls": result.roll_results})
# quick_roll:
await append_turn(..., {"quick_roll": roll_data})
```

Fonte de verdade única após reload = histórico persistido.

---

## Fortuna re-roll

Fluxo:

1. `/roll` falha → histórico +1
2. `/roll/narrate/stream` → **sem** append em applyMeta (fix)
3. Fortuna `/roll/fortune-reroll` → applyRollResponse +1 (novo resultado)
4. `/roll/narrate/stream` → **sem** append duplicado

Entradas na aba Rolagens: falha original + sucesso/falha do re-roll (2 mecânicas distintas) — comportamento desejado.

---

## Teste unitário sugerido

Arquivo: `frontend/src/lib/session/rollHistory.ts` + `rollHistory.test.ts`

```typescript
// Simula fluxo bugado
let history = [];
history = appendRolls(history, rollResponse.roll_results);
history = appendRolls(history, narrateDone.roll_results); // must NOT happen in applyMeta
expect(history).toHaveLength(1);
```

---

## Arquivos afetados

| Arquivo | Mudança |
|---------|---------|
| `frontend/src/hooks/useSessionPlay.ts` | Remover append de applyMeta; rebuild on load |
| `frontend/src/lib/session/rollHistory.ts` | Novo helper testável (opcional mas recomendado) |
| `frontend/src/lib/session/rollHistory.test.ts` | Cobertura duplicação + rebuild |

Sem mudanças backend necessárias para o fix principal.
