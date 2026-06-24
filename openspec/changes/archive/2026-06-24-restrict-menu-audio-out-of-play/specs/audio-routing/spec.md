# Spec: audio-routing

**Change:** `restrict-menu-audio-out-of-play`  
**Capability:** `audio-routing` (modificada)

---

## MODIFIED Requirements

### Requirement: Theme tracks MUST play on non-game pages

A trilha de menu (Theme) SHALL tocar **somente** quando o jogador está em uma rota de meta-jogo explicitamente permitida. Na tela de jogo (`/play/...`), a trilha de menu MUST NOT iniciar nem continuar.

Rotas permitidas: `/`, `/login`, `/register`, `/verify-email`, `/character`, `/campaigns`, `/progression`, `/session/end`, `/session/death`, `/landing`.

#### Scenario: Jogador na tela de campanhas

- **Dado** que o jogador está autenticado em `/campaigns` e o áudio não está silenciado
- **Quando** a página carrega (após interação que desbloqueia autoplay)
- **Então** a trilha menu toca em loop com volume ambiente baixo

#### Scenario: Jogador entra na sessão de jogo

- **Dado** que a trilha menu está tocando em `/campaigns`
- **Quando** o jogador navega para `/play/{sessionId}`
- **Então** a reprodução para imediatamente e não reinicia enquanto em `/play/`

#### Scenario: Rota fora da allowlist

- **Dado** que o jogador está em rota não listada (ex.: `/settings`)
- **Quando** a página carrega
- **Então** nenhuma trilha menu toca

---

### Requirement: Tension tracks MUST play when LLM signals tension

A trilha de tensão SHALL tocar apenas quando o pathname está sob `/play/` **e** o turn response inclui `scene_mood: "tensão"`. Fora de `/play/`, `scene_mood: "tensão"` MUST be ignored.

#### Scenario: GM emite tensão durante sessão

- **Dado** que o jogador está em `/play/{sessionId}` com som ativo
- **Quando** o SSE `done` retorna `scene_mood: "tensão"`
- **Então** a trilha de tensão toca em loop

#### Scenario: GM encerra tensão

- **Dado** que a trilha de tensão está tocando em `/play/{sessionId}`
- **Quando** o response inclui `scene_mood: "normal"`
- **Então** a reprodução para

---

### Requirement: Audio MUST stop on logout

Ao fazer logout, qualquer trilha em reprodução SHALL parar imediatamente.

#### Scenario: Logout na tela de campanhas

- **Dado** que a trilha menu está tocando
- **Quando** o jogador faz logout
- **Então** `audioManager.stop()` é chamado e o áudio cessa
