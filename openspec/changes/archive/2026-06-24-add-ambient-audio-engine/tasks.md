# Tasks: add-ambient-audio-engine

## Fase 1 — Assets e build (pré-requisito de tudo)

- [x] **T1** Mudar build context do service `frontend` em `docker-compose.yml` de `./frontend` para `.` (project root) e ajustar `dockerfile:` para `frontend/Dockerfile`
- [x] **T2** Em `frontend/Dockerfile` (stage `builder`): adicionar `COPY audio ./public/audio/` após `COPY . .`
- [x] **T3** Em `frontend/package.json`: adicionar script `"prepare:audio": "mkdir -p public/audio && cp ../audio/*.mp3 public/audio/"`
- [x] **T4** Em `.gitignore`: adicionar `frontend/public/audio/` com comentário explicativo
- [x] **T5** Smoke check: `test -f public/audio/Solo\ RPG\ Theme.mp3` no Dockerfile builder (falha cedo se arquivos ausentes)

## Fase 2 — Sinal LLM + backend

- [x] **T6** Em `Docs/gm-system-prompt.md`: adicionar instrução de `[MUSICA]` com payload, critérios de cena tensa e exemplos CORRETO/ERRADO
- [x] **T7** Em `backend/app/services/gm_orchestrator.py`: adicionar `scene_mood: str | None = None` ao `TurnResult`
- [x] **T8** Em `gm_orchestrator._handle_signal`: case `"MUSICA"` → `result.scene_mood = payload.get("mood")`
- [x] **T9** Em `stream_turn` done payload: incluir `"scene_mood": result.scene_mood`
- [x] **T10** Em `process_turn` retorno: incluir `scene_mood` no `TurnResult` retornado (já incluído via dataclass)

## Fase 3 — Frontend audio engine

- [x] **T11** Criar `frontend/src/lib/audio/audioManager.ts`: singleton module com `play(category)` e `stop()`; tracks mapeadas por categoria; autoplay retry em `NotAllowedError`; volume ambiente baixo (menu ~30%, tensão ~22%)
- [x] **T12** Criar `frontend/src/hooks/useAudioPlayer.ts`: hook que expõe `setMood(mood)` chamando o singleton; cleanup `stop()` on unmount opcional
- [x] **T13** Em `frontend/src/app/providers.tsx`: adicionar `AudioRoutingProvider` que usa `usePathname` para tocar `"menu"` fora de `/play/...` e `stop()` dentro
- [x] **T14** Em `frontend/src/hooks/useSessionPlay.ts`: ao processar turn response SSE (`done`), chamar `setMood(scene_mood)` se presente
- [x] **T15** Em `AuthContext` (logout handler): chamar `audioManager.stop()`

## Fase 4 — Validação

- [x] **T16** Lint / TypeScript check: nenhum erro
- [ ] **T17** Validar manualmente: navegar para login → theme toca; entrar em sessão → silêncio; LLM emite tensão → tension track toca; LLM emite normal → silêncio; logout → silêncio; voltar para campanhas → theme toca

## Dependências

- T1 + T2 + T3 antes de T5
- T6 antes de T8 (contexto do que o sinal significa)
- T7 antes de T8, T9, T10
- T11 antes de T12, T13, T14, T15
- T16 e T17 ao final
