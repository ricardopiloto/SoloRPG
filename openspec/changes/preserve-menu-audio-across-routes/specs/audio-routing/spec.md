# Spec delta: audio-routing

**Change:** `preserve-menu-audio-across-routes`

---

## MODIFIED Requirements

### Requirement: Theme tracks MUST play on non-game pages

A trilha de menu (Theme) SHALL tocar **somente** quando o jogador está em uma rota de meta-jogo explicitamente permitida. Na tela de jogo (`/play/...`), a trilha de menu MUST NOT iniciar nem continuar. **Ao navegar entre rotas de meta-jogo allowlisted sem passar por `/play/`, a mesma instância de reprodução MUST continuar sem reiniciar do zero.**

Rotas permitidas: `/`, `/login`, `/register`, `/verify-email`, `/character`, `/campaigns`, `/progression`, `/session/end`, `/session/death`, `/landing`.

#### Scenario: Jogador na tela de campanhas

- **Dado** que o jogador está autenticado em `/campaigns` e o áudio não está silenciado
- **Quando** a página carrega (após interação que desbloqueia autoplay)
- **Então** a trilha menu toca em loop com volume ambiente baixo

#### Scenario: Jogador entra na sessão de jogo

- **Dado** que a trilha menu está tocando em `/campaigns`
- **Quando** o jogador navega para `/play/{sessionId}`
- **Então** a reprodução para imediatamente e não reinicia enquanto em `/play/`

#### Scenario: Navegação entre telas de meta-jogo sem reinício

- **Dado** que a trilha menu está tocando em `/character`
- **E** o jogador não está silenciado
- **Quando** o jogador navega para `/campaigns` ou `/progression` (sem passar por `/play/`)
- **Então** a mesma reprodução continua sem `stop()` seguido de novo `Audio`
- **E** a faixa não recomeça do segundo zero

#### Scenario: Retorno da sessão para lobby inicia menu

- **Dado** que o jogador estava em `/play/{sessionId}` sem trilha menu
- **Quando** navega para `/campaigns` (rota allowlisted)
- **Então** a trilha menu inicia (primeiro `play("menu")` após saída da sessão)

#### Scenario: Rota fora da allowlist

- **Dado** que o jogador está em rota não listada (ex.: `/settings`)
- **Quando** a página carrega
- **Então** nenhuma trilha menu toca
