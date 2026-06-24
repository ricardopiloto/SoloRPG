# Tasks: fix-progression-skill-advance-count

## Fase 1 — Backend: persistência de avanços

- [x] **T1** Reescrever `apply_skill_advance()` em `backend/app/rules/careers.py` com update imutável (nova lista + novos dicts, sem mutação in-place)
- [x] **T2** Adicionar `skill_advances_by_name(skills)` no mesmo módulo (ou `rules/skills.py`) somando avanços por nome
- [x] **T3** Usar `skill_advances_by_name()` em `get_progression_options()` para `current_advances`
- [x] **T4** Chamar `flag_modified(char, "skills")` em `purchase_skill_advance()` após atribuir `char.skills`

## Fase 2 — Testes

- [x] **T5** Teste unitário: 4× `apply_skill_advance` na mesma perícia → `advances == 4` na lista retornada
- [x] **T6** Teste unitário: `skill_advances_by_name` com entradas duplicadas soma corretamente
- [x] **T7** Estender `test_api_progression_after_xp` (ou novo teste): 4 POSTs `/progression/skill` → `current_advances == 4`, `xp_spent == 20`, `skills` persistido após reload do DB

## Fase 3 — Frontend copy

- [x] **T8** Em `frontend/src/app/progression/page.tsx`, trocar `· possuído` por `· adquirido` no bloco de talentos

## Fase 4 — Validação manual

- [ ] **T9** Na UI `/progression`: comprar a mesma perícia 3–4 vezes e confirmar que `atual +N` incrementa a cada compra e que XP disponível cai corretamente
- [ ] **T10** Confirmar que talento já comprado exibe `· adquirido` e permanece desabilitado

## Dependências

- T1 antes de T5 e T7
- T2 antes de T3 e T6
- T8 independente do backend (pode paralelizar após aprovação)
