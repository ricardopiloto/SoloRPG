# Design: fix-wfrp-success-levels

## Regra WFRP4e (níveis de sucesso/falha)

Em teste d100, quando `roll <= target` (sucesso):

```
níveis = 1 + (target - roll) // 10
```

Interpretação por **dezenas** (como descrito pelo jogador):

- Dezena do alvo: `floor(target / 10)` → 32 → **3**
- Dezena do dado: `floor(roll / 10)` → 3 → **0**
- Margem em dezenas: `3 - 0 = 3` — coincide com `1 + (32-3)//10 = 3`

O `+1` base representa o sucesso mínimo (passou no teste); cada dezena adicional de margem soma +1 nível.

Em falha (`roll > target`):

```
níveis = 1 + (roll - target) // 10
```

---

## Onde está o bug hoje

| Camada | Comportamento | Alvo 32, dado 3 |
|--------|---------------|-----------------|
| `backend/tests.py` `resolve_test` | ✅ `1 + (32-3)//10 = 3` | 3 |
| `useSessionPlay.appendRolls` | ❌ `floor((32-3)/10) = 2` | **2** |
| `handleDiceRollComplete` (quick-roll) | ✅ `Math.abs(res.levels)` | 3 |
| `DiarySidebar` label | ❌ `nívels` plural | texto errado |

**Causa:** `appendRolls` descarta `levels` do JSON e aplica fórmula sem o `+1` base WFRP.

---

## Correção

### Frontend

```typescript
// appendRolls — usar servidor
levels: r.levels ?? 1,

// NUNCA:
levels: Math.abs(Math.floor((r.target! - r.roll!) / 10)),
```

Adicionar `levels?: number` em `TurnResponse["roll_results"]`.

### Plural PT-BR

```typescript
// i18n ou helper
function formatSuccessLevels(n: number): string {
  if (n <= 0) return "";
  return n === 1 ? "(1 nível)" : `(${n} níveis)`;
}
```

### Backend (clareza + testes)

```python
def test_success_levels_target_32_roll_3():
    r = resolve_test(32, roll=3)  # need roll override
    assert r.success
    assert r.levels == 3
```

Nota: `resolve_test(32, ...)` usa attribute 32 as base — para teste fixo usar `roll=3` com target computado separadamente ou passar attribute+advances que yield target 32.

Actually resolve_test(attribute_value, skill_advances, modifier, roll=3) with attribute 32, no advances → target 32, roll 3 → levels 3.

---

## Fluxo de dados

```
resolve_test() → levels: 3
       │
       ▼
roll_results[].levels  (API / SSE)
       │
       ├── appendRolls → rollHistory[].levels  (FIX: usar campo)
       └── DiarySidebar → "Sucesso (3 níveis)"  (FIX: i18n)
```

Single source of truth: **backend only**.

---

## Relação com fix-roll-history-duplication

Ao reconstruir histórico de `metadata.rolls`, preservar campo `levels` do payload persistido — não recalcular no cliente.
