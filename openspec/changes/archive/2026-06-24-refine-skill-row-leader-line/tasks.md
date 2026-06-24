# Tasks: refine-skill-row-leader-line

- [x] **T1** Em `CharacterSidebar.tsx`: adicionar linha de cabeçalho (`skill-row-header`) com colunas Nome / Atrib. / Adv. / Alvo acima da lista de perícias
- [x] **T2** Refatorar cada botão de perícia para grid 4 colunas: nome+leader, atributo (sigla), avanços (incl. 0), alvo (`target`)
- [x] **T3** Coluna Atributo: exibir `s.linked_attribute` (ex: `Dex`, `S`) — nunca o valor numérico do atributo
- [x] **T4** Em `globals.css`: estilos `.skill-row`, `.skill-row-header`, `.skill-row-name`, `.skill-row-leader`, `.skill-row-attr`, `.skill-row-adv`, `.skill-row-target`
- [x] **T5** Leader line: `border-bottom dashed` com opacidade ~25% dentro da célula Nome, entre texto truncado e borda da coluna
- [x] **T6** Chaves i18n adicionadas em `messages/pt-BR.json` para cabeçalhos das colunas
- [x] **T7** Nome trunca via `truncate`; colunas Attr/Adv/Alvo com largura fixa e `text-right`
- [x] **T8** Lint / TypeScript check: nenhum erro
