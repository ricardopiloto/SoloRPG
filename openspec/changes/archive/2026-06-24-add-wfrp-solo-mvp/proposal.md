# Change: WFRP Solo MVP — Especificação completa da solução

## Why

Jogadores de RPG de mesa frequentemente não conseguem jogar por falta de grupo ou GM disponível. Soluções existentes (livros-jogo, chatbots de roleplay) não combinam profundidade mecânica WFRP4e, imersão narrativa contínua e memória persistente entre sessões. Este change define todas as capabilities necessárias para construir o MVP descrito em `Docs/product-brief.md`.

## What Changes

- Define 9 capabilities do MVP: GM sintético, motor de regras WFRP4e, gestão de personagem, orquestração de sessão, gestão de campanha, memória narrativa, camadas de identidade, assets visuais e interface web.
- Estabelece o protocolo de sinais LLM↔backend (`[TESTE]`, `[IMAGEM]`, `[FIM_SESSAO]`, etc.) como contrato normativo.
- Fixa separação de responsabilidades: regras determinísticas em código, narrativa na LLM, memória em banco de dados.
- Documenta decisões arquiteturais (Next.js, FastAPI/Python ou Fastify/Node, PostgreSQL + pgvector, model-agnostic LLM, Flux 1.1 Pro assíncrono).
- Define escopo explícito fora do MVP (multiplayer, insanidade/corrupção, monetização, app nativo, dificuldade configurável).

## Impact

- Affected specs: `synthetic-gm`, `wfrp-rules-engine`, `character-management`, `session-orchestration`, `campaign-management`, `narrative-memory`, `identity-layers`, `visual-assets`, `web-interface` (todas novas)
- Affected code: greenfield — frontend Next.js, backend API, PostgreSQL + pgvector, integrações LLM e geração de imagens
- Source documents: `Docs/product-brief.md`, `Docs/gm-system-prompt.md`, `Docs/technical-research.md`, `Docs/brainstorming-session-2026-06-07-0212.md`
