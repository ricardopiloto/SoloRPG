## MODIFIED Requirements

### Requirement: Animação 3D via BabylonJS + AmmoJS (Bullet Physics)
O sistema SHALL renderizar a animação de rolagem de dados d100 usando o package `@3d-dice/dice-box`, executando BabylonJS + AmmoJS com canvas **onscreen** montado dentro de um host inline no chat-log — conforme padrão `DiceRoller.rollInChat()` do protótipo Open Design.

#### Scenario: Dados rolam dentro do chat-log
- **WHEN** o jogador clica em "Rolar dado" durante um teste
- **THEN** um bloco `.chat-roll-entry` aparece dentro de `div.chat-log` (componente `ChatLog`), com canvas 3D visível numa área de ~280px de altura centralizada no log — **sem** overlay `position: fixed` cobrindo a viewport

#### Scenario: Animação fisicamente precisa
- **WHEN** o dado é rolado
- **THEN** o d100 é lançado com física Bullet (gravidade, bounce, spin), para suavemente e exibe sombras — visual equivalente ao showcase `dice-roll.html`

#### Scenario: Configuração alinhada ao protótipo
- **WHEN** o `DiceBox` é inicializado para rolagem inline
- **THEN** usa `offscreen: false`, `themeColor: '#C9973A'`, `background: 'transparent'`, `scale: 9.4` e demais parâmetros de física do `dice.mjs` do protótipo

---

### Requirement: Tema visual WFRP
O sistema SHALL aplicar tema dourado WFRP aos dados 3D e ao bloco inline de rolagem.

#### Scenario: Paleta consistente com protótipo
- **WHEN** a animação inline é exibida no chat-log
- **THEN** o stage tem fundo escuro com borda accent, label/meta em font-mono, e dados com `themeColor: #C9973A`

---

### Requirement: Fallback 2D para motion/WebGL
O sistema SHALL exibir fallback 2D **dentro do mesmo bloco inline** quando animação 3D não estiver disponível.

#### Scenario: Fallback no chat-log
- **WHEN** `prefers-reduced-motion: reduce` está ativo ou WebGL indisponível
- **THEN** o bloco `.chat-roll-entry` exibe animação 2D simplificada (sem canvas WebGL) no mesmo local do chat-log, com resultado textual ao final

---

## ADDED Requirements

### Requirement: Bloco inline de rolagem no chat (`ChatRollEntry`)
O sistema SHALL renderizar rolagens de dados como entrada dedicada no log de chat, espelhando a estrutura do protótipo (`chat-roll-label`, `chat-roll-meta`, `dice-inline-stage`, `dice-canvas-host`, `dice-result-block`).

#### Scenario: Estrutura visual do bloco
- **WHEN** uma rolagem inicia
- **THEN** o chat exibe label do teste (ex.: "Teste de Agilidade"), meta com modificadores e alvo, stage 3D, e após settle um bloco de resultado com total formatado e veredito sucesso/falha

#### Scenario: Formato d100 no resultado
- **WHEN** a rolagem d100 completa com valor 47
- **THEN** o resultado exibe `Rolagem: 47 (40 + 7)` e, se houver alvo, veredito "Sucesso · SL N" ou "Falha"

#### Scenario: Fade-out e remoção
- **WHEN** o resultado é exibido por ~2 segundos (`holdMs`)
- **THEN** o bloco aplica fade-out (~400ms), remove-se do DOM, e dispara callback para continuar fluxo da sessão (API + narração GM)

---

### Requirement: Auto-scroll para rolagem ativa
O sistema SHALL rolar suavemente o chat-log para tornar visível a entrada de rolagem recém-inserida.

#### Scenario: Scroll na inserção
- **WHEN** uma entrada `dice-roll` é adicionada ao chat
- **THEN** `ChatLog` faz scroll suave até o bloco de rolagem — sem re-scroll contínuo durante a animação física

---

### Requirement: Preload de assets na sessão
O sistema SHALL pré-carregar o `DiceBox` ao entrar na rota `/play/[sessionId]` para reduzir delay no primeiro roll.

#### Scenario: Primeiro roll sem delay longo
- **WHEN** o jogador entra na sessão e aguarda ~2s antes do primeiro roll
- **THEN** o primeiro roll não exibe "Preparando dados 3D…" por mais de 1 segundo (assets já inicializados)

---

## REMOVED Requirements

### Requirement: Overlay fullscreen fixo para dados 3D
O overlay `Dice3DOverlay` com `position: fixed; inset: 0; z-index: 200` cobrindo toda a viewport é REMOVIDO — substituído pelo bloco inline `ChatRollEntry` dentro de `.chat-log`.

#### Scenario: Sem overlay fullscreen
- **WHEN** o jogador rola um dado na sessão
- **THEN** nenhum elemento `position: fixed` cobre header, sidebars ou input de chat; apenas o bloco inline no chat-log exibe a animação
