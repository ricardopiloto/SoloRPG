# Spec delta: session-ui

**Change:** `fix-roll-history-duplication`

---

## MODIFIED Requirements

### Requirement: Histórico de rolagens na barra lateral

A barra lateral direita SHALL exibir uma aba "Rolagens" com o histórico cronológico de todas as rolagens da sessão atual, incluindo: atributo/perícia testada, valor rolado (d100), alvo numérico, resultado (sucesso/falha) e níveis de sucesso/falha. Cada resolução mecânica de dado SHALL aparecer **exactly once** no histórico — o cliente MUST NOT registrar o mesmo `roll_results` novamente ao processar a narração pós-teste (`/roll/narrate/stream`). Ao carregar uma sessão com histórico persistido, o frontend SHALL reconstruir a aba Rolagens a partir de `SessionTurn.metadata.rolls` (turnos GM) e `metadata.quick_roll` (turnos system).

#### Scenario: Rolagem de teste exibida

- **WHEN** o jogador realiza um teste de Agilidade com resultado 34 (alvo 40, sucesso 1 nível)
- **THEN** a aba Rolagens mostra **one** entry for that roll after narration completes
- **AND** does NOT show a duplicate entry with the same roll and target

#### Scenario: Dois testes de Percepção na mesma sessão

- **WHEN** o jogador completa dois testes GM de Percepção (rolar + narrar, duas vezes)
- **THEN** a aba Rolagens lists exactly **two** entries
- **AND** not four or other multiples

#### Scenario: Rolagem de ataque exibida

- **WHEN** o jogador realiza um ataque corpo a corpo
- **THEN** a aba Rolagens mostra the roll, alvo, hit/miss and damage if hit — once per mechanical resolution

#### Scenario: Aba Rolagens é a padrão durante sessão

- **WHEN** o jogador está em sessão ativa
- **THEN** a aba "Rolagens" é selecionada por padrão na barra lateral direita

#### Scenario: Nenhuma rolagem ainda

- **WHEN** nenhum teste foi realizado na sessão
- **THEN** a aba Rolagens exibe mensagem "Nenhuma rolagem ainda."

#### Scenario: Histórico restaurado ao reabrir sessão

- **WHEN** o jogador abre `/play/{sessionId}` de uma sessão pausada que já tinha rolagens
- **THEN** a aba Rolagens is populated from persisted turn metadata
- **AND** the entry count matches the number of mechanical rolls stored in history

#### Scenario: Quick-roll espontânea

- **WHEN** o jogador executa um quick-roll fora de teste GM pendente
- **THEN** a aba Rolagens registra uma única entrada marcada como espontânea
- **AND** does not duplicate on subsequent GM turns
