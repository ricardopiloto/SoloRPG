# Proposal: fix-wfrp-success-levels

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `add-game-chat-ux`, `fix-roll-history-duplication`

---

## Why

Dois problemas na exibição de **níveis de sucesso/falha** WFRP4e:

1. **Plural incorreto em PT-BR:** a aba Rolagens usa `nívels` (grafia inválida). O correto é **nível** (singular) / **níveis** (plural).

2. **Contagem errada no frontend:** `useSessionPlay.appendRolls()` **ignora** `levels` do backend e recalcula com:

   ```typescript
   Math.abs(Math.floor((target - roll) / 10))
   ```

   Exemplo reportado: alvo **32**, dado **3** → deveria ser **3 níveis** de sucesso; a UI mostra **2**.

   O backend (`resolve_test`) já aplica a regra WFRP correta:

   ```python
   levels = 1 + (target - roll) // 10   # sucesso → 1 + 2 = 3
   ```

   Equivalente à regra por **dezenas**: dezena do alvo (3) menos dezena do dado (0), **mais 1** de sucesso base — total 3.

---

## What Changes

### 1. Frontend — confiar no backend

- `appendRolls()`: usar `r.levels` retornado pela API; remover recálculo local incorreto.
- Tipos `TurnResponse.roll_results` e `RollHistoryEntry`: incluir campo `levels?: number`.
- Quick-roll já usa `res.levels` — manter.

### 2. UI — plural PT-BR

- `DiarySidebar`: substituir template `nível${n > 1 ? "s" : ""}` por i18n com plural correto (`nível` / `níveis`).
- Opcional: chave `session.successLevels` em `pt-BR.json`.

### 3. Backend — testes e clareza

- Testes unitários explícitos em `test_rules.py`:
  - alvo 32, dado 3 → sucesso, **3 níveis**
  - alvo 40, dado 34 → sucesso, **1 nível**
  - falha com margem conhecida
- Comentário ou helper `success_levels(target, roll)` documentando regra WFRP (dezenas + base 1).
- `to_llm_text`: trocar `nível(is)` por pluralização legível (`1 nível` / `3 níveis`).

### 4. Spec deltas

- `wfrp-rules-engine`: MODIFIED cálculo de níveis com cenário 32 vs 3.
- `session-ui`: MODIFIED exibição na aba Rolagens (valor correto + plural PT-BR).

---

## Out of Scope

- Alterar fórmula de dano em combate (já usa `test.levels` do backend).
- Refatorar overlay de dados 3D para mostrar dezenas separadas.
- Traduzir `to_llm_text` completo para i18n backend.

---

## Acceptance Criteria

1. Alvo 32, dado 3, sucesso → aba Rolagens mostra **Sucesso (3 níveis)**.
2. Plural correto: 1 nível, 2 níveis, 3 níveis — nunca `nívels`.
3. Frontend não recalcula `levels` — usa valor do servidor.
4. Testes backend cobrem caso 32/3 e regressões.
5. `openspec validate fix-wfrp-success-levels --strict` passa.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| `roll_results` antigos sem campo `levels` | Fallback: usar `levels` do backend ou 1 se ausente; não recalcular com fórmula errada |
| Histórico reconstruído (`fix-roll-history-duplication`) | `buildRollHistoryFromTurns` deve mapear `levels` de metadata |
