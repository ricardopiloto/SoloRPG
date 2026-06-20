# Spec: chat-scroll

**Capability:** Scroll contido no ChatLog durante a sessão de jogo

---

## MODIFIED Requirements

### Requirement: CHAT-SCROLL-01 — Scroll restrito ao container `.chat-log`

O scroll automático de novas mensagens e de entradas de dado MUST ocorrer **somente** dentro do elemento `.chat-log`. O scroll SHALL NOT propagar para ancestrais (`body`, `html`, `window`).

O componente `ChatLog` MUST usar `scrollTop`/`scrollTo` diretamente no elemento container `.chat-log` (via `ref`) em vez de `scrollIntoView` nos elementos filhos.

**Motivação:** `scrollIntoView` propaga para o primeiro ancestral scrollável — que pode ser o `body` quando a cadeia flex perde `min-h-0`. O scroll explícito via `scrollTop`/`scrollTo` no container elimina essa fragilidade.

#### Scenario: Nova mensagem chega durante sessão

**Dado** que o jogador está na tela de sessão e o `.chat-log` tem conteúdo suficiente para overflow  
**Quando** o GM envia uma nova mensagem (nova entrada em `entries`)  
**Então** o `.chat-log` deve rolar suavemente até o final  
**E** `document.body.scrollTop` deve permanecer `0`  
**E** `window.scrollY` deve permanecer `0`

#### Scenario: Entrada de dado inline aparece

**Dado** que o backend solicita um teste e uma entrada `kind: "dice-roll"` é adicionada  
**Quando** o `useEffect` detecta o novo `rollId`  
**Então** o `.chat-log` SHALL rolar até centralizar o anchor do dado usando `getBoundingClientRect` para cálculo relativo ao container  
**E** a janela principal não deve mover  
**E** o canvas 3D do DiceOverlay (elemento `absolute inset-0` relativo a `.chat-column`) MUST permanecer visualmente fixo e não scrollar com o `.chat-log`

#### Scenario: DiceOverlay cobre o chat durante a rolagem

**Dado** que `diceRolling === true` e o DiceOverlay está visível  
**Quando** o `.chat-log` ajusta seu `scrollTop`  
**Então** o backdrop e o canvas 3D do DiceOverlay MUST permanecer fixos cobrindo toda a `.chat-column`  
**E** os elementos do DiceOverlay (`#wfrp-dice-stage`, backdrop, UI de resultado) SHALL ter `position: absolute` relativo a `.chat-column` e não participar do fluxo de scroll do `.chat-log`

#### Scenario: Primeira carga da sessão

**Dado** que o jogador abre `/play/[sessionId]` com histórico de mensagens  
**Quando** o `ChatLog` monta pela primeira vez  
**Então** o `.chat-log` deve rolar instantaneamente até o final  
**E** a janela principal não deve mover

---

### Requirement: CHAT-SCROLL-02 — Outras telas não são afetadas

As páginas `/character`, `/campaigns`, `/landing` e `/` SHALL continuar com scroll natural do documento. A correção MUST ser limitada ao componente `ChatLog` e ao layout `.game-shell`, sem alterar o `<body>` global.

#### Scenario: Usuário acessa `/character`

**Dado** que o usuário navega para a tela de personagem  
**Quando** a página tem conteúdo longo  
**Então** o scroll do documento deve funcionar normalmente (sem regressão)

---

### Requirement: CHAT-SCROLL-03 — `chat-input-area` permanece fixo no rodapé

`div.chat-input-area` é um irmão de `.chat-log` dentro de `.chat-column` e MUST permanecer visualmente fixo no rodapé da coluna de chat durante qualquer auto-scroll. O auto-scroll SHALL operar exclusivamente dentro do `.chat-log` e SHALL NOT deslocar o `chat-input-area`.

#### Scenario: Auto-scroll após nova mensagem do GM

**Dado** que o GM enviou uma nova mensagem e `entries` foi atualizado  
**Quando** o `useEffect` de `ChatLog` dispara o scroll para o fundo  
**Então** o `.chat-log` SHALL rolar internamente até o fim da lista  
**E** o `div.chat-input-area` MUST permanecer no rodapé da `.chat-column`, com `getBoundingClientRect().top` maior que 80% da altura do viewport

#### Scenario: Estado após a rolagem de dados

**Dado** que o DiceOverlay foi exibido e o `onDone` foi chamado  
**Quando** o DiceOverlay some e o chat retoma visibilidade  
**Então** o `div.chat-input-area` MUST estar visível e posicionado no rodapé  
**E** o formulário de input SHALL estar acessível sem necessidade de scroll manual

---

## Cross-references

- `add-game-chat-ux` — implementou o `scrollIntoView` original (task 2.1–2.4)
- `refactor-inline-chat-dice-roll` — adicionou o scroll para dado inline (task 1.4)
- `add-immersive-session-ui` — não cobre scroll; não há conflito
