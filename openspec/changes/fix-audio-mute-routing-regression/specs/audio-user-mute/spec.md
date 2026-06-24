# Spec delta: audio-user-mute

**Change:** `fix-audio-mute-routing-regression`

---

## MODIFIED Requirements

### Requirement: Muted state MUST block all audioManager playback

Quando `isMuted()` é `true`, `audioManager.play(category)` SHALL retornar sem criar elemento `<audio>` para qualquer categoria (`menu`, `tensao`). **Chamadas `play()` assíncronas iniciadas antes do mute MUST NOT commitar reprodução após `setMuted(true)` ou `stop()`.**

#### Scenario: play bloqueado globalmente

- **Dado** que `wfrp-audio-muted` é `true`
- **Quando** `audioManager.play("menu")` ou `play("tensao")` é chamado
- **Então** nenhum áudio inicia

#### Scenario: setMuted(true) interrompe imediatamente

- **Dado** que qualquer trilha está em reprodução
- **Quando** `setMuted(true)` é invocado
- **Então** `stop()` é chamado e a flag persiste em `localStorage`

#### Scenario: Mute durante play assíncrono in-flight

- **Dado** que `play("menu")` foi chamado e `await audio.play()` ainda não completou
- **Quando** o jogador clica em Silenciar (`setMuted(true)`)
- **Então** nenhum áudio permanece audível após a resolução do `await`
- **E** `currentCategory` permanece `null`

#### Scenario: Silenciar no lobby impede reinício ao navegar

- **Dado** que o jogador silenciou o áudio em `/character`
- **Quando** navega para `/campaigns` ou `/progression`
- **Então** nenhuma trilha menu inicia até o jogador clicar em Ativar som

#### Scenario: Mute é global entre rotas com botão visível

- **Dado** que o jogador silenciou em `/campaigns` via `AudioMuteButton`
- **Quando** navega para `/character` ou `/progression` (AppShell)
- **Então** o botão continua mostrando estado silenciado
- **E** nenhuma trilha toca até desmutar
