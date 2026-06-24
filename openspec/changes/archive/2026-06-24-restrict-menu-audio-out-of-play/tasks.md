# Tasks: restrict-menu-audio-out-of-play

## Fase 1 — Roteamento explícito

- [x] **T1** Criar `frontend/src/lib/audio/audioRoutes.ts` com `isInGameRoute`, `isMenuAudioRoute` e constante `MENU_AUDIO_ROUTES`
- [x] **T2** Testes unitários em `frontend/src/lib/audio/audioRoutes.test.ts` cobrindo `/play/uuid`, `/campaigns`, `/`, rotas desconhecidas

## Fase 2 — Integração de roteamento

- [x] **T3** `AudioRoutingProvider` em `providers.tsx`: substituir denylist por allowlist (T1); respeitar `isMuted()`
- [x] **T4** `audioManager.play`: no-op quando `isMuted()` ou `category === "menu"` em rota de jogo
- [x] **T5** `useAudioPlayer.setMood`: `usePathname`; `tensão` só em rota de jogo; respeitar `isMuted()`

## Fase 3 — Mute do jogador

- [x] **T6** `audioManager`: `isMuted()`, `setMuted(boolean)`, persistência `localStorage` (`wfrp-audio-muted`); `stop()` ao silenciar
- [x] **T7** Hook `useAudioMute()` com `muted` + `toggleMute` (lê estado inicial do `audioManager` / storage)
- [x] **T8** `play/[sessionId]/page.tsx`: botão ao lado de Pausar; i18n `session.muteAudio` / `session.unmuteAudio` em `pt-BR.json`
- [x] **T9** Testes unitários: `play()` no-op quando muted; `setMuted(false)` não toca em `/play/` sem `scene_mood`

## Fase 4 — Validação

- [x] **T10** TypeScript / lint sem erros
- [ ] **T11** Validar manualmente:
  - `/campaigns` ou `/character` → theme toca (som ativo)
  - Entrar `/play/...` → theme para imediatamente
  - GM emite tensão → tension toca; `normal` → silêncio
  - Clicar **Silenciar** → qualquer trilha para; novo `scene_mood` tensão não inicia
  - Clicar **Ativar som** em `/play/` → silêncio até novo sinal ou sair para lobby
  - Clicar **Silenciar** em `/play/`, pausar e ir a `/campaigns` → menu não toca enquanto muted
  - Reativar som em `/campaigns` → menu retoma
  - Refresh com muted salvo → continua sem áudio
  - Logout → silêncio

## Dependências

- T1 antes de T2–T5
- T6 antes de T3, T5, T7–T9
- T7 antes de T8
- T10–T11 ao final
