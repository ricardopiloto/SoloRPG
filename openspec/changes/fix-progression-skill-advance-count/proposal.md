# Proposal: fix-progression-skill-advance-count

**Data:** 2026-06-24  
**Status:** Draft  
**Relacionado:** `add-wfrp-solo-mvp`, `wfrp-rules-engine`, `character-management`

---

## Why

Na tela de **Progressão** (`/progression`), o rótulo `atual +N` das perícias não reflete compras repetidas do mesmo avanço. Exemplo reproduzido com Helena Krauss: após **4 compras** de Percepção (+1), a UI continua exibindo `atual +1`, enquanto o XP gasto (`xp_spent`) sobe corretamente (20 XP deduzidos).

Investigação local confirmou que o problema **não é só de exibição**:

```
xp_spent: 20
skills: [..., {"name": "Percepção", "advances": 1, ...}]
current_advances (API): 1
```

Ou seja, o backend **cobra XP** mas **não persiste** incrementos subsequentes no JSON `player_characters.skills`.

### Causa raiz

`apply_skill_advance()` em `backend/app/rules/careers.py`:

1. **Primeira compra** de uma perícia inexistente → `append` de novo objeto → SQLAlchemy detecta mudança → persiste (`advances: 1`).
2. **Compras seguintes** → encontra a perícia e **muta o dict in-place** dentro de uma cópia rasa da lista (`updated = list(skills)`). A atribuição `char.skills = updated` não dispara persistência confiável da coluna JSON — o ORM trata o valor como equivalente ao anterior.

Resultado: `xp_spent` incrementa (coluna escalar), mas `advances` fica congelado em `1` após a primeira compra.

### Pedido adicional (copy)

Na mesma tela, talentos já adquiridos exibem `· possuído`. O texto deve ser **`· adquirido`**.

---

## What Changes

### Fix 1 — Persistência imutável de avanços de perícia

Reescrever `apply_skill_advance()` para retornar uma **nova lista com novos dicts** (sem mutação in-place). Opcionalmente chamar `flag_modified(char, "skills")` em `purchase_skill_advance()` como reforço.

### Fix 2 — Leitura defensiva de avanços

Em `get_progression_options()`, agregar avanços por nome de perícia (soma) para tolerar duplicatas legadas no JSON e garantir que `current_advances` reflita o total real.

### Fix 3 — Testes de regressão

- Unitário: 4 chamadas sequenciais a `apply_skill_advance` → `advances == 4`.
- Integração API: 4 POSTs em `/progression/skill` → `current_advances == 4` e `xp_spent == 20`.
- Verificar que rolagens/tests usam o valor persistido (sidebar e `resolve_test`).

### Fix 4 — Copy de talentos na UI

Em `frontend/src/app/progression/page.tsx`, trocar `possuído` por `adquirido` no rótulo de talentos owned.

---

## Capabilities

### Modified Capabilities

- **wfrp-rules-engine** — persistência correta de avanços de perícia entre compras
- **web-interface** — contador `atual +N` confiável na tela de progressão; copy "adquirido" para talentos

---

## Impact

| Área | Alterações |
|------|------------|
| `backend/app/rules/careers.py` | `apply_skill_advance()` imutável; helper opcional `skill_advances_by_name()` |
| `backend/app/services/character.py` | `get_progression_options()` soma avanços; `flag_modified` em compra |
| `backend/tests/` | Testes unitários + integração multi-compra |
| `frontend/src/app/progression/page.tsx` | `possuído` → `adquirido` |

---

## Non-Goals

- Reparo automático de `xp_spent` vs. avanços em personagens já corrompidos (jogador pode re-comprar ou ajuste manual no DB)
- Progressão de carreira (tier / atributos) — fora do escopo deste bug
- Internacionalização do rótulo `atual +N` (permanece hardcoded em PT-BR como hoje)

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| Update imutável + `flag_modified` | Só `flag_modified` com mutação in-place | Imutável é mais seguro e testável; evita regressão em outras colunas JSON |
| Soma defensiva na leitura | Confiar só no fix de escrita | Protege dados legados com entradas duplicadas no JSON |
| Copy inline na página | i18n `progression.talentAcquired` | Escopo mínimo; i18n pode vir em change futura |

---

## Open Questions

| Questão | Decisão assumida |
|---------|-----------------|
| Personagens em produção com XP gasto mas avanços errados? | Documentar no CHANGELOG; sem migration automática no MVP |
| Exibir avanços totais incluindo os da criação? | Sim — `atual +N` = total de avanços da perícia na ficha (comportamento atual, só corrigir o valor) |
