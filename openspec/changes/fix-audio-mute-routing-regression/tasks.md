# Tasks: fix-audio-mute-routing-regression

## Fase 1 — audioManager: cancelamento de play assíncrono + instância única

- [x] **T1** Adicionar `playGeneration` e invalidar em `stop()` / `setMuted(true)`
- [x] **T2** Não atribuir `currentAudio` antes do `await`; commitar `currentAudio`/`currentCategory` só se geração válida, `!isMuted()` e (menu) `!isInGameRoute()`
- [x] **T3** Em commits abortados, `pause()` + `src=""` no elemento `<audio>` local da promise (evitar órfãos audíveis)
- [x] **T4** `cancelInteractionRetry()` em `stop()` — remover listeners de retry e limpar `pendingCategory`

## Fase 2 — AudioRoutingProvider

- [x] **T5** Guardas de roteamento usam `audioManager.isMuted()` síncrono (além de `muted` nas deps para reavaliar ao desmutar)
- [x] **T6** Early-return menu→menu só quando `!audioManager.isMuted()` e menu já tocando (`isAudiblyPlaying()`)

## Fase 3 — Testes

- [x] **T7** Teste: `setMuted(true)` após iniciar `play("menu")` in-flight → nenhuma reprodução ativa
- [x] **T8** Teste: dois `play("menu")` concorrentes (primeiro com `await` atrasado) → uma única instância audível
- [x] **T9** Teste: `setMuted(true)` + `play("menu")` → no-op
- [x] **T10** Teste: dois `play("menu")` sequenciais sem mute → 1 instância (continuidade)
- [x] **T11** Teste: `play("menu")` com pathname `/play/...` → bloqueado

## Fase 4 — Validação manual

- [ ] **T12** Lobby: navegar personagens ↔ campanhas ↔ progressão — **nunca** duas músicas sobrepostas
- [ ] **T13** Lobby: Silenciar em `/campaigns`; navegar para `/character` — permanece silenciado
- [ ] **T14** Lobby com som: entrar em `/play/` — tema para; sair — tema retoma (se não mutado)
- [ ] **T15** Silenciar em `/login` e após login em `/campaigns` — comportamento consistente

## Dependências

- T1–T4 antes de T7–T11
- T5–T6 antes de T12–T15
