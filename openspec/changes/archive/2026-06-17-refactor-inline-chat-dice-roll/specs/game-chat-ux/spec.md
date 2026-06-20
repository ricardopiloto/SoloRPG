## MODIFIED Requirements

### Requirement: Auto-scroll na área de jogo
O sistema SHALL manter auto-scroll no chat-log quando novas mensagens ou rolagens de dados forem adicionadas, focando a entrada mais recente.

#### Scenario: Scroll em nova mensagem narrativa
- **WHEN** o GM envia uma nova resposta narrativa
- **THEN** o chat-log rola suavemente para exibir a mensagem mais recente

#### Scenario: Scroll em rolagem de dados inline
- **WHEN** uma entrada `dice-roll` é inserida no chat-log
- **THEN** o chat-log rola suavemente para centralizar o bloco de rolagem 3D na viewport scrollável do log
