# inventory-prompt-rule Specification

## Purpose
TBD - created by archiving change enforce-inventory-constraints. Update Purpose after archive.
## Requirements
### Requirement: GM MUST restrict item usage to character inventory

The synthetic GM SHALL verify `<inventario>` contents before narrating any physical use of an item by the character.

#### Scenario: Jogador tenta usar item ausente do inventário
- **Dado** que o inventário contém ["Facão (enc 1)", "Algemas (enc 0)"]
- **E** o jogador escreve "Saco minha espada longa e ataco"
- **Então** o GM narra uma resposta que nega o uso da espada longa dentro da ficção
- **E** não narra o ataque com essa arma
- **E** não quebra personagem ou menciona regras/sistema

#### Scenario: Jogador usa item presente no inventário
- **Dado** que o inventário contém ["Espada Longa (enc 2)", "Escudo (enc 2)"]
- **E** o jogador escreve "Empunho minha espada longa"
- **Então** o GM narra o uso normalmente sem restrição

#### Scenario: Jogador usa item do cenário (não inventário)
- **Dado** que o inventário não contém tochas
- **E** o jogador escreve "Pego a tocha que está na parede"
- **Então** o GM pode narrar a aquisição contextual do item
- **E** o item não precisa estar no inventário para essa ação específica

#### Scenario: Jogador tenta usar poção já consumida
- **Dado** que o inventário continha "Poção de Cura (enc 0)" e foi consumida nesta sessão conforme narrado
- **E** o jogador escreve "Bebo outra poção de cura"
- **Então** o GM narra que o personagem não possui mais a poção

