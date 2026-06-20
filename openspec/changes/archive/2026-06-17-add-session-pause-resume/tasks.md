# Tasks: Pausa e retomada de sessão

## 1. Backend — modelo e migração

- [x] 1.1 Em `backend/app/db/models.py`, adicionar em `GameSession`:
  - `paused_at: Mapped[datetime | None]` (DateTime, nullable)
  - `total_paused_seconds: Mapped[int]` (Integer, default 0)
- [x] 1.2 `Base.metadata.create_all` em SQLite-dev recria tabela com os novos campos automaticamente
- [x] 1.3 (Postgres) Documentado no README: `ALTER TABLE game_sessions ADD COLUMN paused_at TIMESTAMPTZ, ADD COLUMN total_paused_seconds INT DEFAULT 0`

## 2. Backend — service

- [x] 2.1 `session_time_remaining_minutes()` refatorado para suportar pausa:
  - Se `paused_at IS NOT None`: congela elapsed no momento da pausa
  - Desconta `total_paused_seconds` do elapsed total
- [x] 2.2 `pause_session(db, session)` implementado:
  - Valida `is_active=True` e `paused_at IS None`
  - Seta `paused_at = now(utc)` e faz commit
- [x] 2.3 `resume_session(db, session)` implementado:
  - Valida `is_active=True` e `paused_at IS NOT None`
  - Incrementa `total_paused_seconds += delta`, zera `paused_at = None`
- [x] 2.4 `start_session()` ajustado:
  - Sessão pausada existente → retorna sessão (sem criar nova)
  - Sessão ativa não-pausada → ValueError (comportamento anterior)
- [x] 2.5 `should_end_session()` ajustado para não encerrar sessão pausada

## 3. Backend — API

- [x] 3.1 `POST /sessions/{id}/pause` — pausa e retorna `SessionDetailOut`
- [x] 3.2 `POST /sessions/{id}/resume` — retoma e retorna `SessionDetailOut`
- [x] 3.3 `GET /sessions/{id}/history` — retorna `list[SessionTurnOut]` em ordem cronológica
- [x] 3.4 `SessionOut` e `SessionDetailOut` incluem campo `paused_at: datetime | None`
- [x] 3.5 `SessionTurnOut` adicionado em `schemas/api.py`
- [x] 3.6 `CampaignOut` inclui `active_session_paused: bool` e `active_session_time_remaining: int | None`
- [x] 3.7 `_campaign_out()` e `_campaign_out_with_session()` passam sessão completa ao invés de só ID

## 4. Frontend — API client

- [x] 4.1 Tipo `SessionDetail` inclui `paused_at?: string | null`
- [x] 4.2 Tipo `Campaign` inclui `active_session_paused?: bool` e `active_session_time_remaining?: number | null`
- [x] 4.3 Tipo `SessionTurnOut` adicionado em `api.ts`
- [x] 4.4 Funções `pauseSession`, `resumeSession`, `getSessionHistory` adicionadas

## 5. Frontend — restauração de histórico

- [x] 5.1 `useSessionPlay.load()` chama `api.getSessionHistory()` ao montar o hook
  - Se há turns → popula `entries` via `turnsToEntries()`, marca `started=true`, `showPrepare=false`
  - Se sem turns → usa `sessionStorage` como fallback (sessão nova)
- [x] 5.2 Função `turnsToEntries()` mapeia roles do banco (`player`, `gm`, `system`) para `ChatEntry`
- [x] 5.3 Se sessão está `paused_at != null`, `resume` é chamado automaticamente ao entrar na tela

## 6. Frontend — botão "Pausar sessão"

- [x] 6.1 Botão "⏸ Pausar" adicionado no header de `play/[sessionId]/page.tsx`
  - Desabilitado quando `loading=true` ou `diceVisible=true`
- [x] 6.2 `pauseSession()` adicionado ao hook: chama API e navega para `/campaigns`

## 7. Frontend — tela de campanhas

- [x] 7.1 Sessão pausada exibe badge "⏸ Pausada" + tempo restante congelado
- [x] 7.2 Botão "Retomar sessão" em vez de "Iniciar sessão" para sessões pausadas
- [x] 7.3 Navegar para `/play/{sessionId}` → hook auto-resume ao carregar

## 8. Testes

- [x] 8.1 `test_api_session_pause_resume`: pausa → duplicata retornada → resume → erros esperados
- [x] 8.2 `test_api_session_history`: turns persistidos são retornados com roles corretos
- [x] 8.3 `pytest tests/test_api_integration.py` — 5/5 passando
- [x] 8.4 `npm run build` — build sem erros de TypeScript
