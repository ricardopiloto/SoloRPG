# Spec: audio-user-mute

**Change:** `add-global-audio-mute-button`  
**Capability:** `audio-user-mute` (modificada)

---

## ADDED Requirements

### Requirement: Mute control MUST be available on out-of-game screens

The application SHALL expose the same global mute toggle used in play sessions on lobby and auth screens where menu ambient audio may play.

#### Scenario: Jogador silencia na tela de campanhas

- **Dado** que o jogador está autenticado em `/campaigns` e a trilha menu está tocando
- **Quando** clica em **Silenciar** no topnav do `AppShell`
- **Então** o áudio para imediatamente
- **E** `wfrp-audio-muted` permanece `true` após navegar para outras rotas de lobby

#### Scenario: Jogador reativa som no lobby

- **Dado** que o áudio está silenciado e o jogador está em `/character`
- **Quando** clica em **Ativar som** no topnav
- **Então** a trilha menu inicia se a rota estiver na allowlist e autoplay permitido

#### Scenario: Login sem AppShell

- **Dado** que o visitante está em `/login`
- **Quando** visualiza a página
- **Então** o botão **Silenciar** / **Ativar som** está visível e funcional

---

### Requirement: Mute control MUST remain in play session header

The play session screen SHALL keep the mute toggle adjacent to the pause control; behavior MUST match the lobby control (shared component, shared `localStorage` state).

#### Scenario: Mesmo estado entre sessão e lobby

- **Dado** que o jogador silenciou o áudio em `/play/{sessionId}`
- **Quando** pausa e navega para `/campaigns`
- **Então** o topnav mostra **Ativar som** (muted)
- **E** nenhuma trilha menu inicia até reativar
