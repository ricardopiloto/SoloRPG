# Change: DeepSeek como LLM padrão do GM

## Why

O código atual usa `LLM_PROVIDER=mock` por default e mantém adapters Anthropic/DeepSeek/model-agnostic. O jogador já configurou DeepSeek no `.env`, mas streaming não está exposto ao frontend e o product-brief v1.1 ainda referencia Claude — a decisão do projeto é usar **DeepSeek** como LLM de produção e desenvolvimento.

## What Changes

- DeepSeek como provider padrão (`LLM_PROVIDER=deepseek`, `LLM_MODEL=deepseek-chat`)
- Streaming real via API DeepSeek (`stream: true`) exposto como endpoint SSE
- Remover dependência de mock LLM no fluxo de sessão (mock apenas para testes)
- Documentação de env, modelos (`deepseek-chat`, `deepseek-reasoner`) e limites de contexto
- Atualizar `openspec/project.md` e `.env.example` para DeepSeek

## Impact

- Affected specs: `synthetic-gm`, `dev-infrastructure`
- Affected code: `backend/app/config.py`, `backend/app/llm/adapter.py`, `backend/app/api/routes.py`, `frontend/src/lib/api.ts`, `frontend/src/app/page.tsx`, `.env.example`
- Nota: diverge do product-brief v1.1 §9 (Claude único) — DeepSeek é a decisão técnica atual do projeto
