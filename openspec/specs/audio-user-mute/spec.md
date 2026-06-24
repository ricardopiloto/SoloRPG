# audio-user-mute Specification

## Purpose
TBD - created by archiving change restrict-menu-audio-out-of-play. Update Purpose after archive.
## Requirements
### Requirement: Muted state MUST block all audioManager playback

Quando `isMuted()` é `true`, `audioManager.play(category)` SHALL retornar sem criar elemento `<audio>` para qualquer categoria (`menu`, `tensao`).

#### Scenario: play bloqueado globalmente

- **Dado** que `wfrp-audio-muted` é `true`
- **Quando** `audioManager.play("menu")` ou `play("tensao")` é chamado
- **Então** nenhum áudio inicia

#### Scenario: setMuted(true) interrompe imediatamente

- **Dado** que qualquer trilha está em reprodução
- **Quando** `setMuted(true)` é invocado
- **Então** `stop()` é chamado e a flag persiste em `localStorage`

---

### Requirement: Mute preference MUST be readable on app init

Na inicialização do `audioManager` (primeiro uso no cliente), o estado MUST ser carregado de `localStorage` para que refresh e nova aba respeitem a escolha do jogador.

#### Scenario: Init com mute salvo

- **Dado** que `localStorage["wfrp-audio-muted"] === "true"`
- **Quando** a aplicação carrega e o `AudioRoutingProvider` avalia a rota
- **Então** `playMenu()` não inicia áudio

