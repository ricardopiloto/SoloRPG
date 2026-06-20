# Tasks: update-session-pausable-ux

## 1. Frontend — `pt-BR.json`

- [x] 1.1 Renomear chave `session.notPausable` para `session.pauseHint` e alterar valor para `"Use ⏸ no topo para pausar."`
- [x] 1.2 Atualizar `session.prepareBody`: remover `"A sessão não pode ser pausada."` e substituir por `"Você pode pausar e retomar quando quiser."`
  - Novo valor: `"Duração estimada: ~{minutes} minutos. Você pode pausar e retomar quando quiser."`

## 2. Frontend — `page.tsx`

- [x] 2.1 Na linha que exibe `t("session.notPausable")`, atualizar para `t("session.pauseHint")`

## 3. Documentação técnica

- [x] 3.1 `openspec/project.md` linha 51: atualizado para `Sessions are pausable; player can pause and resume at any time. Duration is announced before start.`
- [x] 3.2 `README.md`: atualizado `"timer visível, não pausável"` para `"timer visível, pausável"`
- [x] 3.3 `Docs/product-brief.md`: atualizado para `"sessões pausáveis (pausa e retomada a qualquer momento)"`
- [x] 3.4 `Docs/mvp-validation-checklist.md`: atualizado para `"sessão pausável (botão ⏸ no header, retomada automática ao re-entrar)"`

## 4. Validação

- [x] 4.1 `npm run build` — zero erros TypeScript ✓
- [x] 4.2 Verificar que nenhum outro uso de `session.notPausable` permanece no código — nenhum encontrado em código fonte ativo ✓
  - Residual apenas em `openspec/changes/add-wfrp-solo-mvp/` (documentos históricos arquivados — não alterar)
- [ ] 4.3 Verificar visualmente: overlay de início mostra texto correto sobre pausabilidade
- [ ] 4.4 Verificar visualmente: hint abaixo do input mostra "Use ⏸ no topo para pausar." quando não há teste pendente
