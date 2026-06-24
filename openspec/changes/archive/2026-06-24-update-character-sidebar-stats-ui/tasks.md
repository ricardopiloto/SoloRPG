# Tasks: update-character-sidebar-stats-ui

## 1. Backend — catálogo e quick roll

- [x] 1.1 Criar `backend/app/rules/skills.py` com `SKILL_CATALOG` unificando mapeamentos existentes
- [x] 1.2 Refatorar `gm_orchestrator.SKILL_ATTRIBUTES` e `careers.PROGRESSION_SKILLS` para importar do catálogo
- [x] 1.3 Adicionar `GET /rules/skills` retornando lista ordenada `{ name, linked_attribute }`
- [x] 1.4 Alterar `execute_quick_roll`: perícia no catálogo mas ausente na ficha → `advances = 0`
- [x] 1.5 Testes: quick roll de perícia não possuída; quick roll de perícia inválida rejeitada

## 2. Frontend — constantes e API

- [x] 2.1 Criar `frontend/src/lib/wfrp-attributes.ts` com `ATTRIBUTE_ORDER`, `ATTRIBUTE_LABELS` (tooltips EN)
- [x] 2.2 Adicionar `api.listSkills()` consumindo `GET /rules/skills`
- [x] 2.3 Helper `computeSkillTarget(character, skillName, catalog)` usando atributo vinculado + avanços

## 3. Frontend — componentes UI

- [x] 3.1 Criar `AttributeCards.tsx`: grid 5×2 compacto; sigla menor no topo; valor grande centralizado; dezena sublinhada (bônus WFRP); tooltip; click rollable
- [x] 3.2 CSS em `globals.css`: `.attribute-card` compacto (`p-1`, `min-w-0`), underline na dezena, hover rollable
- [x] 3.3 Refatorar `CharacterSidebar`: substituir grid de atributos por `AttributeCards`
- [x] 3.4 Refatorar seção de perícias: `CollapsibleSection` (padrão Inventário) com catálogo completo; linhas `rollable` abrem `QuickRollPopover`
- [x] 3.5 Corrigir cálculo de alvo de perícia (remover `Ag` hardcoded)

## 4. i18n e acessibilidade

- [x] 4.1 Chaves i18n: título da seção via `character.skills` existente (sem placeholder/botão de select)
- [x] 4.2 `aria-label` nos cards de atributo incluindo nome completo + valor

## 5. Validação

- [x] 5.1 `npm run build` — zero erros TypeScript
- [x] 5.2 `pytest backend/tests/test_quick_roll.py` — passa incluindo novo caso
- [ ] 5.3 Revisão visual: grid 5×2 cabe na sidebar; sigla menor no topo; valor grande; dezena sublinhada (ex. 34 → 3̲4); tooltip ao hover
- [ ] 5.4 Revisão funcional: lista colapsável exibe todas as perícias do catálogo; rolar perícia não possuída funciona
- [ ] 5.5 Revisão funcional: quick roll bloqueado durante teste pendente do GM (regressão)
