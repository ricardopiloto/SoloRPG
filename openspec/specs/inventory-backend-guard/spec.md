# inventory-backend-guard Specification

## Purpose
TBD - created by archiving change enforce-inventory-constraints. Update Purpose after archive.
## Requirements
### Requirement: Backend MUST inject system note when missing inventory item is detected

Before sending the message to the LLM, the orchestrator SHALL heuristically verify whether the player action references an item absent from inventory. If detected, it SHALL inject a `[NOTA DO SISTEMA]` into the message context.

#### Scenario: Ação com item ausente detectado
- **Dado** que `character.trappings = [{"name": "Facão"}, {"name": "Mochila"}]`
- **E** `player_action = "Saco minha espada longa e ataco o guarda"`
- **Quando** `_check_inventory_reference` é chamado
- **Então** retorna uma nota não-nula mencionando "espada longa" e listando o inventário atual

#### Scenario: Ação com item presente — sem injeção
- **Dado** que `character.trappings = [{"name": "Espada Longa"}, {"name": "Escudo"}]`
- **E** `player_action = "Empunho minha espada longa"`
- **Quando** `_check_inventory_reference` é chamado
- **Então** retorna `None` (sem injeção)

#### Scenario: Ação sem verbo de uso — sem injeção
- **Dado** qualquer inventário
- **E** `player_action = "Olho ao redor para ver se há saída"`
- **Quando** `_check_inventory_reference` é chamado
- **Então** retorna `None` (sem falso positivo)

#### Scenario: Normalização de acentos e capitalização
- **Dado** que `character.trappings = [{"name": "Espada Longa"}]`
- **E** `player_action = "saco minha ESPADA longa"`
- **Quando** `_check_inventory_reference` é chamado
- **Então** retorna `None` (item encontrado apesar de variação de caso)

### Requirement: Inventory check MUST run in process_turn and stream_turn

The heuristic inventory check SHALL run in both player turn entry points (`process_turn` and `stream_turn`).

#### Scenario: Integração em process_turn
- **Dado** que a verificação retorna uma nota
- **Quando** `process_turn` monta a mensagem para o LLM
- **Então** a nota precede a ação do jogador na mensagem enviada ao LLM

#### Scenario: Sem impacto em narrate_roll
- **Dado** que o turno está em fase `awaiting_narrate`
- **Quando** `narrate_roll` ou `stream_narrate_roll` é chamado
- **Então** nenhuma verificação de inventário é feita (ação já foi processada no turno inicial)

