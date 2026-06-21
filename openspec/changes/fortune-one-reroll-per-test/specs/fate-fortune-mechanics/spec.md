## MODIFIED Requirements

### Requirement: FORT-01 — Ponto de Fortuna re-rola teste falho

O sistema SHALL permitir gastar 1 Ponto de Fortuna para re-rolar um teste mal-sucedido. Fortuna SHALL NOT conceder bônus numérico (+10) como alternativa. **Cada instância de teste GM SHALL permitir no máximo um re-roll com Fortuna**, mesmo que o personagem ainda possua Pontos de Fortuna restantes na sessão.

#### Scenario: Re-roll bem-sucedido com Fortuna

- **WHEN** o jogador falha um teste GM pendente
- **AND** `fortune_current > 0`
- **AND** `fortune_reroll_used` é `false` para esse teste
- **AND** o jogador escolhe gastar Fortuna
- **THEN** o sistema SHALL deduzir 1 Ponto de Fortuna
- **AND** SHALL executar nova rolagem com as mesmas regras de alvo/modificador
- **AND** SHALL marcar `fortune_reroll_used = true` para esse teste

#### Scenario: Segundo re-roll no mesmo teste bloqueado

- **WHEN** o jogador já usou Fortuna para re-rolar o teste atual (`fortune_reroll_used = true`)
- **AND** a nova rolagem também falhou
- **THEN** o sistema SHALL NOT oferecer novo re-roll com Fortuna para esse teste
- **AND** SHALL NOT deduzir Fortuna adicional
- **AND** o jogador SHALL resolver o teste com o resultado final da última rolagem

#### Scenario: Fortuna disponível em teste subsequente

- **WHEN** o jogador falhou um teste, usou Fortuna uma vez, e o GM emite um novo `[TESTE]`
- **THEN** `fortune_reroll_used` SHALL resetar para o novo teste
- **AND** o jogador MAY gastar Fortuna novamente se `fortune_current > 0`

#### Scenario: Fortuna indisponível

- **WHEN** o jogador falha um teste e `fortune_current = 0`
- **THEN** o sistema SHALL NOT oferecer re-roll via Fortuna
- **AND** o teste SHALL ser resolvido com a rolagem original
