# Change: Pausa e retomada de sessão

## Why

Atualmente, uma sessão de jogo só pode ser encerrada com `[FIM_SESSAO]` (que atribui XP e fecha definitivamente) ou abandonada fechando o navegador — nesse caso o timer continua correndo em segundo plano e a sessão fica "fantasma" para o jogador. Não há como o jogador salvar o progresso, fechar a aba e retomar exatamente de onde parou, incluindo o histórico de chat visível e o timer congelado no instante da pausa.

## What Changes

- **Modelo `GameSession`:** novos campos `paused_at` (datetime nullable) e `total_paused_seconds` (int, default 0) para congelar o timer durante a pausa.
- **Backend — service:** funções `pause_session()` e `resume_session()` que registram pausa/retomada e ajustam o tempo restante corretamente.
- **Backend — API:** dois novos endpoints:
  - `POST /sessions/{id}/pause` — pausa a sessão ativa (retorna `SessionDetail` atualizado)
  - `POST /sessions/{id}/resume` — retoma uma sessão pausada (retorna `SessionDetail` atualizado)
- **Backend — `start_session`:** se a campanha já possui uma sessão pausada (não encerrada), o endpoint `POST /campaigns/{id}/sessions` retorna essa sessão existente em vez de criar uma nova — evitando duplicatas.
- **Backend — `turn_history` como fonte de verdade para exibição:** endpoint `GET /sessions/{id}/history` retorna todos os `SessionTurn` formatados para o frontend recontruir o chat.
- **Frontend — hook `useSessionPlay`:** substituir `sessionStorage` por carregamento do histórico via API; ao retomar sessão pausada, popular `entries` com o histórico persistido no banco.
- **Frontend — botão "Pausar sessão":** exibido na interface de jogo; ao clicar chama `PATCH /sessions/{id}/pause`, exibe feedback e navega para `/campaigns`.
- **Frontend — fluxo de "Retomar":** na tela `/campaigns`, sessões pausadas exibem badge "Pausada" e botão "Retomar" (em vez de "Iniciar sessão").

## Impact

- Affected specs: `session-lifecycle`
- Affected code:
  - `backend/app/db/models.py` — adicionar `paused_at`, `total_paused_seconds` em `GameSession`
  - `backend/app/services/session.py` — adicionar `pause_session()`, `resume_session()`, ajustar `session_time_remaining_minutes()`, ajustar `start_session()` para retornar sessão pausada
  - `backend/app/api/routes.py` — adicionar rotas `pause` e `resume`; adicionar `GET /sessions/{id}/history`; ajustar `POST /campaigns/{id}/sessions`
  - `backend/app/schemas/api.py` — adicionar `SessionStatus`, atualizar `SessionDetail`
  - `frontend/src/hooks/useSessionPlay.ts` — carregar histórico via API, remover dependência de `sessionStorage` para estado inicial
  - `frontend/src/app/campaigns/page.tsx` — badge "Pausada" + botão "Retomar"
  - `frontend/src/app/play/[sessionId]/page.tsx` — botão "Pausar sessão"
  - `frontend/src/lib/api.ts` — adicionar funções `pauseSession`, `resumeSession`, `getSessionHistory`
- New DB columns: `game_sessions.paused_at`, `game_sessions.total_paused_seconds`
- No breaking changes to existing endpoints (novos endpoints e campos additive)
