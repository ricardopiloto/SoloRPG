# Tasks: DeepSeek LLM

- [x] 1.1 Alterar defaults em `config.py`: `llm_provider=deepseek`, `llm_model=deepseek-chat`
- [x] 1.2 Implementar streaming real no `DeepSeekAdapter` (chunks da API, não split por palavra)
- [x] 1.3 Expor endpoint SSE para turnos de sessão
- [x] 1.4 Consumir SSE no frontend durante narração GM
- [x] 1.5 Atualizar `.env.example` e `openspec/project.md`
- [x] 1.6 Testes de integração com mock HTTP da API DeepSeek
