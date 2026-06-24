# Proposal: show-skill-target-in-sidebar

**Data:** 2026-06-23  
**Status:** Draft  
**Relacionado:** `refine-skill-row-target-display`, `skill-row-wfrp-advance-format`

---

## Why

Na sidebar de personagem, cada linha de perícia mostra no lado direito o formato sheet WFRP — ex: `4+[BS]` para 4 avanços em Ballistic Skill, ou apenas `[BS]` quando não há avanços. Esse formato reflete a ficha de papel, mas **não diz imediatamente o valor alvo da rolagem** — o jogador precisa fazer a conta mentalmente (33 base BS + 4 = 37).

O usuário quer ver diretamente o **total calculado** (atributo base + avanços), igual ao que já é passado para o `QuickRollPopover` como `target`. Isso torna a sidebar funcional em vez de decorativa: o número visível é exatamente o que será rolado.

---

## Comportamento atual

```
Atirar (Armas de Fogo)    4+[BS]   ← avanços + atributo (formato ficha)
Furtividade               [Ag]     ← só o atributo (0 avanços)
```

## Comportamento desejado

```
Atirar (Armas de Fogo)    37       ← BS(33) + 4 avanços = 37
Furtividade               34       ← Ag(34) + 0 = 34
```

Se o valor calculado for 0 (atributo zerado, sem avanços), exibir `0` — nunca string vazia ou oculto.

---

## What Changes

Em `CharacterSidebar.tsx`, na renderização de cada skill row:

- Substituir `{formatSkillRowMeta(s.linked_attribute, advances)}` por `{String(target)}`
- A variável `target` já existe no escopo (`computeSkillTarget(...)`)
- O import de `formatSkillRowMeta` pode ser removido se não houver outros usos no arquivo

A função `formatSkillRowMeta` em `wfrp-attributes.ts` **não será deletada** — ela ainda pode ser usada por outros contextos e seus testes permanecem válidos.

---

## Capabilities

### Modified Capabilities

- **quickroll-ux**: valor exibido na linha de perícia da sidebar é o alvo numérico total

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/components/character/CharacterSidebar.tsx` | `formatSkillRowMeta(...)` → `String(target)` na skill row |
| `frontend/src/lib/wfrp-attributes.ts` | Sem alteração (função mantida para uso futuro) |
| `frontend/src/app/globals.css` | Sem alteração (`.skill-row-meta` ainda usado para estilo) |

---

## Non-Goals

- Remover `formatSkillRowMeta` da base de código
- Alterar a ficha de personagem ou a tela de progressão
- Mostrar atributo + avanços separados na sidebar (ex: `33+4`) — o pedido é o total apenas
- Alterar o comportamento do `QuickRollPopover` (já recebe `target` correto)
