# Tasks: preserve-menu-audio-across-routes

## Fase 1 — audioManager idempotente

- [x] **T1** Adicionar `currentCategory: AudioCategory | null` e helper `isPlaying()` em `audioManager.ts`
- [x] **T2** Em `play(category)`: early-return se `currentCategory === category` e áudio ativo; setar `currentCategory` só após `play()` bem-sucedido
- [x] **T3** Em `stop()` e `setMuted(true)`: limpar `currentCategory`

## Fase 2 — Roteamento (opcional, recomendado)

- [x] **T4** Em `AudioRoutingProvider`: rastrear pathname anterior; evitar `playMenu()` redundante ao navegar entre duas rotas allowlisted consecutivas

## Fase 3 — Testes

- [x] **T5** Teste unitário: dois `play("menu")` → uma instância `Audio`, sem reinício
- [x] **T6** Teste unitário: `play("menu")` depois `play("tensao")` → substitui categoria
- [x] **T7** Teste unitário: `stop()` depois `play("menu")` → novo elemento (reinício legítimo)

## Fase 4 — Validação manual

- [ ] **T8** Lobby: iniciar menu em `/character`, navegar para `/campaigns` e `/progression` — música **não** reinicia do zero
- [ ] **T9** Entrar em `/play/...` — menu para; sair para `/campaigns` — menu **inicia**; navegar entre lobby — **não** reinicia
- [ ] **T10** Com mute ativo, navegar entre lobby — silêncio; desmutar em `/campaigns` — menu inicia uma vez

## Dependências

- T1–T3 antes de T5–T7
- T8–T10 dependem de T1–T3 (T4 opcional)
