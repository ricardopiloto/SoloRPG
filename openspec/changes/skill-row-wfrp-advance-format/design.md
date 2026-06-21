# Design: skill-row-wfrp-advance-format

## Context

A sidebar de perícias (`CharacterSidebar`) exibe meta à direita via `formatSkillRowMeta()` em `wfrp-attributes.ts`. A change `refine-skill-row-target-display` introduziu formato `[Attr] +N` (ex.: `[Fel] +4`). Jogadores de WFRP esperam avanços antes do atributo: `N+[Attr]` (ex.: `4+[Fel]`).

Cálculo de alvo (`computeSkillTarget`) permanece inalterado: `atributo + avanços + modificador`.

## Goals / Non-Goals

**Goals:**

- Exibir meta WFRP `{N}+[{Attr}]` quando `N > 0`.
- Exibir apenas `[{Attr}]` quando `N === 0` (sem `0+` ou `+0`).
- Manter layout nome à esquerda, meta à direita.
- Preservar `aria-label` com avanços, atributo e alvo calculado.

**Non-Goals:**

- Alterar cálculo server-side de quick roll.
- Exibir valor numérico do atributo na linha (ex.: `33`).
- Mudar cards de atributos ou inventário.

## Decisions

### 1. Formato em `formatSkillRowMeta`

**Decisão:**

```typescript
export function formatSkillRowMeta(linkedAttribute: string, advances: number): string {
  const tag = `[${linkedAttribute}]`;
  return advances > 0 ? `${advances}+${tag}` : tag;
}
```

| Antes | Depois |
|-------|--------|
| `Seduzir      [Fel] +4` | `Seduzir      4+[Fel]` |
| `Furtividade  [Ag]` | `Furtividade  [Ag]` |

**Alternativa rejeitada:** Manter `[Attr] +N` — inverte convenção WFRP de ficha.

### 2. Fonte de avanços

Cruzamento de `character.skills[].advances` com catálogo `GET /rules/skills`. Perícia ausente na ficha → 0 avanços → só `[Attr]`, alvo = valor do atributo.

### 3. Estilo

Reutilizar `.skill-row-meta`: `text-wfrp-muted font-mono text-[11px] shrink-0 tabular-nums` — sem alteração de CSS.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Regressão visual em nomes longos | Meta separada à direita com `shrink-0` (padrão existente) |
| Testes de `refine-skill-row-target-display` desatualizados | Atualizar expectativas para novo formato |

## Migration Plan

Deploy frontend-only. Sem migration de backend. Atualizar testes unitários de `formatSkillRowMeta`.

## Open Questions

Nenhuma.
