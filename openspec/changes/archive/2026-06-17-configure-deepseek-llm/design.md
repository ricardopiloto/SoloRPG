# Design: DeepSeek LLM Integration

## Decisions

- **Provider padrão:** `deepseek` via API OpenAI-compatible em `https://api.deepseek.com`
- **Modelo narrativa GM:** `deepseek-chat` (custo/qualidade equilibrado)
- **Modelo alternativo:** `deepseek-reasoner` para sessões complexas (configurável)
- **Streaming:** SSE endpoint `GET /api/sessions/{id}/turn/stream` ou POST com `Accept: text/event-stream`
- **System prompt:** continua carregado de `Docs/gm-system-prompt.md`; injeção de contexto XML inalterada
- **Mock:** disponível apenas com `LLM_PROVIDER=mock` explícito (testes CI)

## Configuração `.env`

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

## Risks

| Risco | Mitigação |
|-------|-----------|
| Latência | Streaming SSE para UX |
| Aderência ao system prompt | Testes de integração com respostas reais |
| Custo | `deepseek-chat` default; reasoner opt-in |
