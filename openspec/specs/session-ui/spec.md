# session-ui Specification

## Purpose
TBD - created by archiving change add-game-chat-ux. Update Purpose after archive.
## Requirements
### Requirement: Renderização Markdown no chat narrativo
Os blocos de narrativa do GM no `ChatLog` SHALL ser renderizados como Markdown, incluindo suporte a negrito, itálico, listas não-ordenadas e separadores horizontais. Linhas do jogador (`player-line`) e mensagens de sistema (`roll-system-msg`) NÃO devem receber renderização Markdown.

#### Scenario: Negrito e itálico visíveis
- **WHEN** o GM emite uma narrativa contendo `**palavra**` ou `_palavra_`
- **THEN** o jogador vê "palavra" em negrito ou itálico, não o texto literal com asteriscos

#### Scenario: Texto do jogador sem Markdown
- **WHEN** o jogador digita uma ação com asteriscos, ex: `*atacar*`
- **THEN** o texto é exibido como digitado, sem renderização Markdown

#### Scenario: Streaming sem flash de símbolos
- **WHEN** tokens chegam em streaming e contêm `**palavra**` incompleto
- **THEN** o Markdown é aplicado apenas ao texto final acumulado; tokens parciais mostram texto puro

---

### Requirement: Auto-scroll para nova mensagem
O chat de jogo SHALL rolar automaticamente para a mensagem mais recente toda vez que uma nova entrada for adicionada, incluindo durante streaming de tokens.

#### Scenario: Nova mensagem do GM
- **WHEN** o GM termina de narrar e uma nova `narrative-block` é adicionada
- **THEN** o chat rola suavemente até a última mensagem

#### Scenario: Streaming em andamento
- **WHEN** tokens chegam em streaming e expandem a última entrada
- **THEN** o chat mantém foco na entrada em expansão (scroll suave, debounced)

#### Scenario: Histórico já carregado ao abrir sessão
- **WHEN** o jogador abre uma sessão com histórico existente
- **THEN** o scroll vai imediatamente (sem animação) para o fim do log antes de qualquer nova mensagem

---

### Requirement: Histórico de rolagens na barra lateral
A barra lateral direita SHALL exibir uma aba "Rolagens" com o histórico cronológico de todas as rolagens da sessão atual, incluindo: atributo/perícia testada, valor rolado (d100), alvo numérico, resultado (sucesso/falha) e níveis de sucesso/falha.

#### Scenario: Rolagem de teste exibida
- **WHEN** o jogador realiza um teste de Agilidade com resultado 34 (alvo 40, sucesso 1 nível)
- **THEN** a aba Rolagens mostra entrada: "Agilidade · 34 vs 40 · Sucesso (1 nível)"

#### Scenario: Rolagem de ataque exibida
- **WHEN** o jogador realiza um ataque corpo a corpo
- **THEN** a aba Rolagens mostra o roll, alvo, hit/miss e dano se acertou

#### Scenario: Aba Rolagens é a padrão durante sessão
- **WHEN** o jogador está em sessão ativa
- **THEN** a aba "Rolagens" é selecionada por padrão na barra lateral direita

#### Scenario: Nenhuma rolagem ainda
- **WHEN** nenhum teste foi realizado na sessão
- **THEN** a aba Rolagens exibe mensagem "Nenhuma rolagem ainda."

