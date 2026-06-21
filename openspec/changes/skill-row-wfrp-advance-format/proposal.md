# Proposal: skill-row-wfrp-advance-format

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `refine-skill-row-target-display` (supersedida visualmente — inverte ordem de avanços e atributo)

---

## Why

Na sidebar de perícias, o jogador precisa ver de forma imediata **quantos avanços possui** em cada perícia e **qual atributo** a compõe — no padrão WFRP de ficha: avanços primeiro, atributo entre colchetes (ex.: `4+[Fel]`). A implementação anterior (`refine-skill-row-target-display`) exibia `[Fel] +4`, que inverte a ordem esperada pelo jogador de WFRP.

## What Changes

- **Formato WFRP na meta da linha:** `{N}+[{Attr}]` quando `N > 0`; apenas `[{Attr}]` quando `N === 0`.
- **Atualizar `formatSkillRowMeta`:** de `[Fel] +4` para `4+[Fel]`.
- **Cálculo de alvo inalterado:** `atributo + avanços + modificador` (quick roll).
- **Acessibilidade:** `aria-label` informa avanços, atributo e alvo calculado.

### Exemplos visuais

| Perícia | Avanços | Atributo | Exibição |
|---------|---------|----------|----------|
| Seduzir | 4 | Fel | `4+[Fel]` |
| Furtividade | 0 | Ag | `[Ag]` |
| Atirar (Arco) | 5 | BS | `5+[BS]` |

## Capabilities

### New Capabilities

- `skill-row-display`: Formato WFRP de avanços + atributo na sidebar de perícias.

### Modified Capabilities

- `web-interface`: Requisito de layout da linha de perícia atualizado para ordem `{N}+[{Attr}]`.

## Impact

| Área | Alterações |
|------|------------|
| Frontend | `wfrp-attributes.ts` (`formatSkillRowMeta`), `CharacterSidebar.tsx`, testes unitários |
| Backend | Nenhum |
