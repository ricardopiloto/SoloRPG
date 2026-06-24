# Spec delta: audio-routing

**Change:** `fix-audio-mute-routing-regression`

---

## MODIFIED Requirements

### Requirement: Theme tracks MUST play on non-game pages

A trilha de menu (Theme) SHALL tocar **somente** quando o jogador está em uma rota de meta-jogo explicitamente permitida **e o áudio não está silenciado**. Na tela de jogo (`/play/...`), a trilha de menu MUST NOT iniciar nem continuar. **A continuidade menu→menu (sem reiniciar do zero) MUST NOT bypassar mute nem rota in-game.**

Rotas permitidas: `/`, `/login`, `/register`, `/verify-email`, `/character`, `/campaigns`, `/progression`, `/session/end`, `/session/death`, `/landing`.

#### Scenario: Jogador na tela de campanhas

- **Dado** que o jogador está autenticado em `/campaigns` e o áudio não está silenciado
- **Quando** a página carrega (após interação que desbloqueia autoplay)
- **Então** a trilha menu toca em loop com volume ambiente baixo

#### Scenario: Jogador entra na sessão de jogo

- **Dado** que a trilha menu está tocando em `/campaigns`
- **Quando** o jogador navega para `/play/{sessionId}`
- **Então** a reprodução para imediatamente e não reinicia enquanto em `/play/`

#### Scenario: Navegação entre telas de meta-jogo sem reinício (som ativo)

- **Dado** que a trilha menu está tocando em `/character` e o áudio **não** está silenciado
- **Quando** o jogador navega para `/campaigns` sem passar por `/play/`
- **Então** a mesma reprodução continua sem reiniciar do zero

#### Scenario: Navegação lobby com áudio silenciado

- **Dado** que o jogador silenciou o áudio em `/character`
- **Quando** navega para `/campaigns`
- **Então** nenhuma trilha inicia e o silêncio é mantido

#### Scenario: Retorno da sessão para lobby inicia menu

- **Dado** que o jogador estava em `/play/{sessionId}` sem trilha menu
- **E** o áudio não está silenciado
- **Quando** navega para `/campaigns`
- **Então** a trilha menu inicia

#### Scenario: Rota fora da allowlist

- **Dado** que o jogador está em rota não listada (ex.: `/settings`)
- **Quando** a página carrega
- **Então** nenhuma trilha menu toca

---

### Requirement: At most one ambient track MUST be audible at any time

The audio engine SHALL ensure that no more than one `HTMLAudioElement` plays ambient audio (`menu` or `tensao`) simultaneously. Starting a new track MUST stop or abort any in-flight or orphaned playback from prior `play()` calls.

#### Scenario: Rapid navigation does not stack tracks

- **Dado** que a trilha menu está iniciando em `/character` (`play()` in-flight)
- **Quando** o jogador navega rapidamente para `/campaigns` antes do primeiro `await` resolver
- **Então** no máximo uma trilha permanece audível
- **E** não há sobreposição de duas faixas Theme

#### Scenario: Category switch replaces previous track

- **Dado** que a trilha menu está tocando
- **Quando** `play("tensao")` é chamado em `/play/{sessionId}`
- **Então** a trilha menu para
- **E** apenas a trilha de tensão toca
