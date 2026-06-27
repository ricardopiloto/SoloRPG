# Spec delta: session-ui

**Change:** `fix-wfrp-success-levels`

---

## MODIFIED Requirements

### Requirement: Histórico de rolagens na barra lateral

A barra lateral direita SHALL exibir uma aba "Rolagens" com o histórico cronológico de todas as rolagens da sessão atual, incluindo: atributo/perícia testada, valor rolado (d100), alvo numérico, resultado (sucesso/falha) e **níveis** de sucesso/falha conforme calculado pelo backend WFRP4e. A UI MUST use the server-provided `levels` value. Pluralização em PT-BR SHALL use **nível** (singular) and **níveis** (plural) — never invalid forms such as `nívels`.

#### Scenario: Rolagem de teste exibida

- **WHEN** o jogador realiza um teste com alvo 32, resultado 3, sucesso com 3 níveis
- **THEN** a aba Rolagens mostra entrada com **Sucesso (3 níveis)**
- **AND** does NOT show 2 níveis

#### Scenario: Rolagem de ataque exibida

- **WHEN** o jogador realiza um ataque corpo a corpo
- **THEN** a aba Rolagens mostra the roll, alvo, hit/miss and damage if hit

#### Scenario: Singular success level label

- **WHEN** a roll succeeds with exactly 1 level
- **THEN** the label reads **1 nível** (not "1 níveis" or "1 nívels")

#### Scenario: Aba Rolagens é a padrão durante sessão

- **WHEN** o jogador está em sessão ativa
- **THEN** a aba "Rolagens" é selecionada por padrão na barra lateral direita

#### Scenario: Nenhuma rolagem ainda

- **WHEN** nenhum teste foi realizado na sessão
- **THEN** a aba Rolagens exibe mensagem "Nenhuma rolagem ainda."
