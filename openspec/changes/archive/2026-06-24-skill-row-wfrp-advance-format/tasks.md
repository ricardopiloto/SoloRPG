# Tasks: skill-row-wfrp-advance-format

## 1. Helper de formatação

- [x] 1.1 Atualizar `formatSkillRowMeta` em `wfrp-attributes.ts` para `{N}+[{Attr}]` quando `N > 0`, senão `[{Attr}]`
- [x] 1.2 Atualizar JSDoc com exemplos `4+[Fel]` e `[Ag]`

## 2. UI

- [x] 2.1 Confirmar que `CharacterSidebar.tsx` usa `formatSkillRowMeta` sem alteração de layout (nome esquerda, meta direita)
- [x] 2.2 Confirmar `aria-label` inclui avanços, atributo e alvo calculado

## 3. Testes

- [x] 3.1 Teste unitário: perícia com avanços → `4+[Fel]`
- [x] 3.2 Teste unitário: perícia sem avanços → `[Ag]` (sem `0+` ou `+0`)
- [x] 3.3 Teste unitário: avanços altos → `5+[BS]`
- [x] 3.4 `npm run build` sem erros TypeScript

## 4. Validação visual

- [x] 4.1 Pregen Helena: `Armas Corpo a Corpo (Básicas)` → `1+[WS]`
- [x] 4.2 Pregen Tobias: `Conhecimento (Magia)` → `2+[Int]`
- [x] 4.3 Perícias sem avanços → só `[Attr]`, quick roll alvo = atributo
