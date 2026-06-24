# Tasks: show-skill-target-in-sidebar

- [x] **T1** Em `CharacterSidebar.tsx`: substituir `{formatSkillRowMeta(s.linked_attribute, advances)}` por `{String(target)}` na skill row
- [x] **T2** Import de `formatSkillRowMeta` removido (não havia outro uso no arquivo)
- [x] **T3** Lint / TypeScript check: nenhum erro
- [ ] **T4** Validar visualmente: sidebar mostra número inteiro positivo para cada perícia; perícias sem avanços mostram apenas o valor base do atributo *(validação manual)*
