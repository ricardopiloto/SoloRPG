# Tasks: add-skill-name-truncation-tooltip

- [x] **T1** Criar `frontend/src/components/ui/TruncatedText.tsx` com detecção `scrollWidth > clientWidth` e `title` condicional
- [x] **T2** Adicionar `ResizeObserver` no componente para reavaliar truncamento quando a sidebar redimensiona
- [x] **T3** Em `CharacterSidebar.tsx`: substituir `<span className="truncate">` por `<TruncatedText>` na coluna Nome das perícias
- [ ] **T4** Validar: nome curto (ex: "Arrombamento") → sem tooltip; nome longo truncado → tooltip com nome completo no hover *(validação manual)*
- [x] **T5** Lint / TypeScript check: nenhum erro
