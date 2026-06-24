# Tasks: refine-skill-row-target-display

## 1. Helper de formatação

- [x] 1.1 Adicionar `formatSkillRowMeta(linkedAttribute, advances)` em `wfrp-attributes.ts`
- [x] 1.2 Documentar regra: `+N` omitido quando `N === 0`

## 2. UI — CharacterSidebar

- [x] 2.1 Atualizar linhas de perícia: nome à esquerda, meta `[Attr] +N` à direita
- [x] 2.2 `aria-label` com atributo, avanços e alvo calculado
- [x] 2.3 CSS `.skill-row-meta` em `globals.css` (mono, muted, shrink-0)

## 3. Validação

- [x] 3.1 `npm run build` — zero erros TypeScript
- [ ] 3.2 Revisão visual: `Atirar (Arco) [BS] +5` com BS=33 → popover alvo 38
- [ ] 3.3 Revisão visual: perícia sem avanços mostra só `[Ag]`, sem `+0`
- [ ] 3.4 Regressão: quick roll de perícia não possuída usa atributo + 0 avanços
