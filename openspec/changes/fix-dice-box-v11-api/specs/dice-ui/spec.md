## ADDED Requirements

### Requirement: Die notation `"1d100"` para dado percentual WFRP
O sistema SHALL usar a notação `"1d100"` ao chamar `box.roll()`, pois o `d100` é o dado percentual nativo do package e representa tecnicamente os dois dados (dezenas + unidades) embutidos em um único objeto físico.

#### Scenario: Dado d100 é rolado
- **WHEN** o jogador rola um teste de atributo na tela de jogo
- **THEN** o `DiceBox` exibe a animação de um dado percentual (`d100`) — não dois dados d10 separados

#### Scenario: Resultado decomposição para display
- **WHEN** `onRollComplete` dispara e o `roll` do servidor é `47`
- **THEN** o overlay exibe `40 + 7 = 47` decompondo o valor do servidor: `tensDisplay = Math.floor((47-1)/10)*10`, `unitsDisplay = (47-1) % 10` — o valor do dado físico é ignorado

---

## MODIFIED Requirements

### Requirement: Construtor v1.1 com objeto único de config
O sistema SHALL usar a API v1.1 do `@3d-dice/dice-box` para instanciar o `DiceBox` — um único objeto de configuração com `container` como campo, conforme documentação oficial em [fantasticdice.games/docs/usage/config](https://fantasticdice.games/docs/usage/config).

#### Scenario: Sem warning de API legada no console
- **WHEN** a rota `/play/[sessionId]` é carregada e o `DiceBox` é inicializado
- **THEN** o console do browser **não** contém a mensagem "You are using the old API. Dicebox constructor accepts a config object as it's only argument"

#### Scenario: Construtor correto com container no config
- **WHEN** o código do `DiceBoxWrapper` é inspecionado
- **THEN** o `DiceBox` é instanciado como `new DiceBox({ container: "#dice-canvas-mount-point", assetPath: "...", ... })` sem argumento posicional separado

---

### Requirement: Dismiss suave com `hide()` + CSS fade
O sistema SHALL usar `box.hide(className)` ao encerrar a animação, aplicando uma transição CSS de fade-out antes de limpar os dados com `clear()`.

#### Scenario: Fade-out visível ao fechar overlay
- **WHEN** o overlay de dados é dismissado (após resultado exibido por 1.8s)
- **THEN** o canvas de dados aplica a classe `dice-hide` com `opacity: 0; transition: opacity 0.3s ease-out` antes de ser removido — sem corte abrupto

---

## ADDED Requirements

### Requirement: Callbacks definidos no objeto de config
O sistema SHALL definir `onRollComplete` diretamente no objeto de configuração passado ao construtor do `DiceBox`, em vez de atribuí-los como propriedades pós-init.

#### Scenario: Sem atribuição pós-init de callbacks
- **WHEN** o código do `DiceBoxWrapper` é inspecionado
- **THEN** o `onRollComplete` do roll corrente é definido via closure dentro do `roll()` call, sem reatribuir `box.onRollComplete` pós-init com risco de race condition
