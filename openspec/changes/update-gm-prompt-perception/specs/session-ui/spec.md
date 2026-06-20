## ADDED Requirements

### Requirement: Feedback narrativo de quick-roll não solicitado
Quando o jogador executar um quick-roll fora de um teste solicitado pelo GM, a interface SHALL exibir a mensagem de narração do GM (recebida no próximo turno) de forma distinta das ações normais, sinalizando que foi uma verificação espontânea.

#### Scenario: Quick-roll exibido na área de jogo
- **WHEN** o jogador faz um quick-roll e o GM responde na narração seguinte
- **THEN** a área de chat mostra a resposta do GM normalmente, e a aba Rolagens registra a rolagem como "espontânea" (sem contexto de teste pendente)

#### Scenario: Rolagem espontânea marcada no histórico
- **WHEN** o histórico de rolagens exibe uma quick-roll sem teste pendente
- **THEN** a entrada é marcada visualmente como "Espontânea" (ex.: tag ou ícone distinto de um teste solicitado pelo GM)
