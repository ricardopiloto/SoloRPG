# Spec: refine-chat-attribution-visual — Chat Attribution

## Capability: Atribuição visual sutil de autoria no chat da sessão

---

## ADDED Requirements

### Requirement: Blocos GM exibem eyebrow "MESTRE" no início de cada sequência

O `ChatLog` SHALL exibir um label de atribuição "Mestre" acima do primeiro bloco de narrativa de cada sequência consecutiva de turnos do GM. Blocos GM subsequentes na mesma sequência SHALL NOT repetir o label.

#### Scenario: Primeiro bloco GM após entrada do jogador recebe label

- **Dado** que a última entrada não-GM no chat foi uma entrada do tipo `player`
- **Quando** uma entrada `narrative` é renderizada
- **Então** um `div.chat-attribution` com texto "Mestre" SHALL aparecer imediatamente acima do bloco de narrativa

#### Scenario: Segundo bloco GM consecutivo não recebe label

- **Dado** que dois blocos `narrative` estão consecutivos no `entries` sem `player` entre eles
- **Quando** o `ChatLog` é renderizado
- **Então** apenas o primeiro bloco SHALL ter `div.chat-attribution` com "Mestre"
- **E** o segundo bloco SHALL NOT ter nenhum `div.chat-attribution`

#### Scenario: Entrada de rolagem não gera label GM

- **Dado** que há uma sequência: `[narrative, roll, narrative]`
- **Quando** o `ChatLog` é renderizado
- **Então** o primeiro `narrative` SHALL ter label "Mestre"
- **E** o segundo `narrative` (após o `roll`) SHALL ter novo label "Mestre" (quebra de sequência)
- **E** o `roll` SHALL NOT ter label

---

### Requirement: Entradas do jogador exibem eyebrow "VOCÊ" alinhado à direita

O `ChatLog` SHALL exibir um label "Você" acima de cada entrada `player` que inicia uma sequência — alinhado à direita para acompanhar o alinhamento do `player-line`.

#### Scenario: Entrada do jogador recebe label "Você"

- **Dado** que uma entrada `player` está sendo renderizada
- **Quando** é a primeira entrada `player` após qualquer entrada não-player
- **Então** um `div.chat-attribution.chat-attribution--player` com texto "Você" SHALL aparecer acima da linha do jogador

#### Scenario: Label não interfere com alinhamento existente do player-line

- **Dado** que o `player-line` é `text-right` e `ml-auto`
- **Quando** o label "Você" é adicionado
- **Então** o `player-line` SHALL permanecer alinhado à direita inalterado
- **E** o label SHALL ser `text-right` para alinhar com o bloco do jogador

---

### Requirement: Labels de atribuição são visualmente sutis e não copiáveis

Os labels de atribuição SHALL usar tamanho e opacidade que os tornem reconhecíveis mas não dominantes — consistentes com a estética literária do jogo. Labels SHALL ser excluídos da seleção de texto do usuário.

#### Scenario: Estilo visual do label

- **Dado** que um `div.chat-attribution` está renderizado
- **Então** SHALL ter fonte `10px`, uppercase, `letter-spacing: 0.18em`, `opacity` equivalente a `text-wfrp-accent/40`
- **E** SHALL ter `user-select: none` (via `select-none`) para não ser copiado com a narrativa

#### Scenario: Label não domina a narrativa visualmente

- **Dado** que o texto narrativo tem `17px` e cor `text-wfrp-fg`
- **Quando** o label "MESTRE" (`10px`, `accent/40`) é exibido acima
- **Então** o label SHALL ocupar menos destaque visual que qualquer parágrafo da narrativa
