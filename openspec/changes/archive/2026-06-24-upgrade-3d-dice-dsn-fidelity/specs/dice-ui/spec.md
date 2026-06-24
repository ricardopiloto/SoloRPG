## MODIFIED Requirements

### Requirement: Animação 3D via BabylonJS + AmmoJS (Bullet Physics)
O sistema SHALL renderizar a animação de rolagem de dados d100 usando o package `@3d-dice/dice-box`, que executa BabylonJS + AmmoJS em web workers com offscreenCanvas — o mesmo pipeline de física de alta fidelidade recomendado pelo Dice So Nice para uso standalone.

#### Scenario: Animação fisicamente precisa
- **WHEN** o dado é rolado na tela de jogo
- **THEN** dois d10 são lançados a partir da borda do container, ricocheteiam nas paredes, caem por gravidade (Bullet Physics), giram de forma realista e param suavemente — com sombras projetadas e iluminação 3D

#### Scenario: Rendering em thread separada
- **WHEN** a animação de dados roda
- **THEN** a UI do React (chat, botões, etc.) permanece responsiva e sem jank — o BabylonJS opera em web worker com offscreenCanvas isolado

#### Scenario: Fallback onscreen automático
- **WHEN** o browser não suporta OffscreenCanvas (ex: Firefox < 105)
- **THEN** o package usa automaticamente `world.onscreen.js` sem mudança de comportamento visível ao usuário

---

### Requirement: Resultado server-authoritative exibido no overlay
O sistema SHALL exibir o resultado correto do servidor no overlay de texto após a animação completar, independentemente dos valores mostrados nos dados 3D.

#### Scenario: Valor do servidor sempre prevalece
- **WHEN** o backend retorna `roll_results[0].roll = 47` e a física dos dados mostra `63` nas faces
- **THEN** o overlay exibe `47` como resultado do teste; os dados 3D são puramente decorativos

#### Scenario: Callback de finalização
- **WHEN** `onRollComplete` dispara (todos os dados pararam de rolar)
- **THEN** `DiceBoxWrapper` chama `onSettled(props.roll)` com o valor original do servidor, disparando a exibição do overlay de resultado

---

### Requirement: Assets servidos localmente
O sistema SHALL servir os assets do `@3d-dice/dice-box` (workers, physics WASM, temas) a partir de `public/assets/dice-box/` na aplicação Next.js.

#### Scenario: Assets disponíveis em rota /play
- **WHEN** o jogador acessa `/play/[sessionId]` e rola um dado
- **THEN** o `DiceBox` inicializa carregando assets de `/assets/dice-box/` com status HTTP 200; nenhum erro 404 de worker ou WASM

#### Scenario: Assets excluídos do repositório
- **WHEN** o repositório é clonado
- **THEN** `public/assets/dice-box/` está listado no `.gitignore` e não é commitado; o `README` ou script de setup documenta o passo de cópia dos assets

---

### Requirement: Tema visual WFRP
O sistema SHALL aplicar um tema escuro aos dados 3D condizente com a estética do WFRP (Warhammer Fantasy Roleplay).

#### Scenario: Cor escura dos dados
- **WHEN** a animação de dados é exibida
- **THEN** os dados têm cor de base escura próxima a `#1a120b` via `themeColor`, contrastando com o fundo da tela de jogo

---

## ADDED Requirements

### Requirement: Fallback 2D para motion/WebGL
O sistema SHALL usar o overlay 2D (`DiceOverlay2D`) quando o ambiente não suporta animação 3D.

#### Scenario: prefers-reduced-motion
- **WHEN** `window.matchMedia('(prefers-reduced-motion: reduce)').matches` é `true`
- **THEN** `DiceOverlay2D` é exibido em vez de `DiceBoxWrapper`

#### Scenario: WebGL indisponível
- **WHEN** a detecção de WebGL falha
- **THEN** `DiceOverlay2D` é exibido automaticamente sem erro visível

---

## REMOVED Requirements

### Requirement: Geometria d10 manual e física cannon-es (substituídos)
Os requisitos anteriores sobre geometria procedural `CylinderGeometry`, corpo físico `CANNON.Box`, textura canvas por dado e snap quaternion de resultado são REMOVIDOS — substituídos integralmente pelo pipeline do `@3d-dice/dice-box`.
