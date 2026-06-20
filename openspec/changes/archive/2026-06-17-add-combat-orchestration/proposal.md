# Change: Orquestração de combate end-to-end

## Why

Modo COMBATE existe no schema e no system prompt, mas `enter_combat`, iniciativa e `[ESTADO_COMBATE]` não estão ligados ao loop. O product-brief exige turnos visíveis em combate.

## What Changes

- Parser/handler para `[ESTADO_COMBATE]` no orchestrator
- Ativar combate via sinal ou transição detectada; rolar iniciativa server-side
- Avançar turnos; UI mostra turno atual e ordem
- Encerrar combate e voltar a EXPLORACAO
- Injetar estado de combate no contexto DeepSeek

## Impact

- Affected specs: `session-orchestration`, `synthetic-gm`, `web-interface`
- Affected code: `gm_orchestrator.py`, `session.py`, `routes.py`, `page.tsx`, `CharacterSheet.tsx`
