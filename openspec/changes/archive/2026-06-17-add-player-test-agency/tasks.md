# Tasks: Agência nos testes

- [x] 1.1 Persistir `pending_test` JSON na sessão quando GM emite `[TESTE]`
- [x] 1.2 Separar turno em fase `awaiting_roll` vs `narrating`
- [x] 1.3 Criar endpoint `POST /sessions/{id}/roll` (server-side d100)
- [x] 1.4 Retornar resultado ao frontend antes de segunda chamada LLM
- [x] 1.5 Componente UI `TestPromptCard` com botão "Rolar dado"
- [x] 1.6 GM narrates consequência apenas após roll confirmado
- [x] 1.7 Testes E2E do fluxo: sinal → botão → rolagem → narração
