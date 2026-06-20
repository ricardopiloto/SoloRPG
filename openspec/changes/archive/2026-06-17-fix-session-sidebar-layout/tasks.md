# Tasks: Painéis laterais fixos

## 1. Layout da sessão

- [x] 1.1 Alterar container da view `session` para `h-screen overflow-hidden` (ou `h-dvh`)
- [x] 1.2 Fixar asides esquerdo/direito com `h-screen shrink-0` e scroll interno (`overflow-y-auto`)
- [x] 1.3 Restringir scroll da coluna central ao histórico do chat (`flex-1 overflow-y-auto min-h-0`)
- [x] 1.4 Manter header e form de input fixos (`shrink-0`) na coluna central

## 2. Componentes

- [x] 2.1 Ajustar `DiaryPanel` para scroll interno sem propagar ao body
- [x] 2.2 Verificar `InventoryPanel` e `CharacterSheet` em viewport baixa

## 3. Responsividade

- [x] 3.1 Validar layout em viewport ≥ 1024px (3 colunas fixas)
- [x] 3.2 Validar layout mobile: chat scrollável isolado; painéis não arrastam scroll global

## 4. Validação

- [x] 4.1 Teste manual: narrativa longa no chat — painéis laterais permanecem visíveis
- [x] 4.2 Teste manual: diário longo — scroll apenas dentro do painel direito
- [x] 4.3 `npm run build` sem erros TypeScript
