# Proposal: refine-skill-row-target-display

**Data:** 2026-06-20  
**Status:** Draft  
**Escopo:** `frontend/src/components/character/CharacterSidebar.tsx` · `frontend/src/lib/wfrp-attributes.ts`

**Relacionado:** `update-character-sidebar-stats-ui` (lista colapsável de perícias já implementada)

---

## Problema

A seção de perícias na sidebar lista o nome e, quando possuída, apenas `+N` à direita — sem indicar o **atributo vinculado** nem deixar claro como o alvo é composto.

Exemplo atual:
```
Atletismo                    +2
Atirar (Arco)
```

O jogador precisa inferir mentalmente que `Atirar (Arco)` usa BS e somar ao valor do atributo. O `Docs/ux-spec.md` §6.3 prevê formato `Escalar (S) +3`; o pedido atual refine isso para colchetes no atributo.

---

## Solução proposta

Cada linha de perícia na `CollapsibleSection` SHALL exibir:

```
Atirar (Arco) [BS] +5
```

| Parte | Significado | Exemplo |
|---|---|---|
| Nome | Perícia do catálogo | `Atirar (Arco)` |
| `[BS]` | Sigla do atributo vinculado (catálogo backend) | `[BS]` |
| `+5` | Avanços de perícia comprados/obtidos pelo jogador | `+5` (omitido quando 0) |

**Cálculo de alvo (inalterado):** `atributo_vinculado + avanços` → ex.: BS 33 + 5 = **38** no quick roll.

### Regras de exibição

- **Sempre** mostrar `[{linked_attribute}]` após o nome (ou agrupado à direita em `text-wfrp-muted font-mono`)
- **`+N`** somente quando `N > 0` (perícia com avanços na ficha)
- Perícia sem avanços: `Furtividade [Ag]` (sem sufixo `+0`)
- Perícia não possuída mas no catálogo: mesmo formato com `[Attr]`, alvo = valor do atributo + 0
- Quick roll continua usando `computeSkillTarget()` — label visual não altera backend

### Layout sugerido

```
Atirar (Arco)              [BS] +5
Escalar                    [S]
Atletismo                  [Ag] +2
```

Nome à esquerda (truncate se longo); meta `[Attr] +N` à direita, alinhado como inventário.

### Acessibilidade

`aria-label` inclui nome, atributo, avanços e alvo calculado:  
`"Atirar (Arco), BS 33, +5 avanços, alvo 38"`

---

## Não-escopo

- Exibir o valor numérico do atributo na linha (ex.: `33`) — só sigla `[BS]` + avanços
- Alterar cálculo server-side de quick roll
- Mudar formato de atributos (cards) ou inventário

---

## Impacto

- **Frontend:** helper `formatSkillRowMeta`, ajuste de render em `CharacterSidebar`, CSS opcional `.skill-row-meta`
- **Specs:** delta em `web-interface` (MODIFIED skill row scenario)
