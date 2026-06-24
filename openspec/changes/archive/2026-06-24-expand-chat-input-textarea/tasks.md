# Tasks: expand-chat-input-textarea

- [x] **T1** Em `globals.css`: classe `.chat-input-textarea` adicionada com `resize: none`, `field-sizing: content`, `min-height: 2.25rem`, `max-height: 8rem`, `overflow-y: auto`, `line-height: 1.5`
- [x] **T2** Em `play/[sessionId]/page.tsx`: `<input>` substituído por `<textarea name="action" rows={1} className="chat-input-textarea">`
- [x] **T3** `onKeyDown`: Enter sem Shift → `e.preventDefault()` + `form.requestSubmit()`; Shift+Enter → nova linha (comportamento padrão)
- [x] **T4** `onSubmit` atualizado: cast para `HTMLTextAreaElement`; `textarea.value = ""` após envio; `items-end` no flex-container para alinhar botão com a base
- [x] **T5** Lint / TypeScript check: nenhum erro
- [ ] **T6** Validar: digitar texto longo → quebra de linha visível; Enter envia; Shift+Enter adiciona linha; após envio o campo volta a 1 linha *(validação manual)*
