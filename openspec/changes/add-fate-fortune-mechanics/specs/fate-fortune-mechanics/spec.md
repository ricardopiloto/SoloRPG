# Spec: fate-fortune-mechanics

**Capability:** Regras WFRP de Pontos de Destino e Fortuna acoplados

---

## ADDED Requirements

### Requirement: FATE-01 — Ponto de Destino evita ferimento ou morte

O sistema SHALL permitir gastar 1 Ponto de Destino para evitar receber um ferimento ou sobreviver a um golpe que seria mortal. Pontos de Destino SHALL NOT ser restaurados automaticamente.

#### Scenario: Evitar ferimento com Destino disponível

- **WHEN** o GM emite `[ACAO_SISTEMA]` tipo `usar_ponto_destino` com motivo `avoid_wound`
- **AND** o personagem tem `fate_current > 0`
- **THEN** o sistema SHALL deduzir 1 Ponto de Destino
- **AND** SHALL NOT aplicar o incremento de wound pendente
- **AND** SHALL persistir o novo `fate_current`

#### Scenario: Sobreviver a golpe mortal com Destino disponível

- **WHEN** o GM emite `[ACAO_SISTEMA]` tipo `usar_ponto_destino` com motivo `avoid_death`
- **AND** o personagem tem `fate_current > 0`
- **THEN** o sistema SHALL deduzir 1 Ponto de Destino
- **AND** SHALL definir `wounds_current = 1`
- **AND** SHALL NOT marcar o personagem como morto

#### Scenario: Destino esgotado em situação fatal

- **WHEN** ocorre efeito mortal ou ferimento sem Destino disponível (`fate_current = 0`)
- **THEN** o sistema SHALL processar consequências normalmente (ferimento aplicado ou morte)
- **AND** SHALL NOT restaurar Destino em sessões ou campanhas futuras

---

### Requirement: FORT-01 — Ponto de Fortuna re-rola teste falho

O sistema SHALL permitir gastar 1 Ponto de Fortuna para re-rolar um teste mal-sucedido. Fortuna SHALL NOT conceder bônus numérico (+10) como alternativa.

#### Scenario: Re-roll bem-sucedido com Fortuna

- **WHEN** o jogador falha um teste GM pendente
- **AND** `fortune_current > 0`
- **AND** o jogador escolhe gastar Fortuna
- **THEN** o sistema SHALL deduzir 1 Ponto de Fortuna
- **AND** SHALL executar nova rolagem com as mesmas regras de alvo/modificador
- **AND** SHALL retornar resultado da nova rolagem ao chat

#### Scenario: Fortuna indisponível

- **WHEN** o jogador falha um teste e `fortune_current = 0`
- **THEN** o sistema SHALL NOT oferecer re-roll via Fortuna
- **AND** o teste SHALL ser resolvido com a rolagem original

---

### Requirement: FORT-02 — Fortuna acoplada ao Destino vigente

A quantidade de Pontos de Fortuna SHALL ser derivada dos Pontos de Destino **atuais** do personagem no início de cada sessão nova.

#### Scenario: Refresh no início de sessão nova

- **WHEN** uma nova sessão é criada via `start_session()` (não retomada pausada)
- **AND** o personagem tem `fate_current = N`
- **THEN** o sistema SHALL definir `fortune_current = N` e `fortune_max = N`

#### Scenario: Destino gasto reduz Fortuna na próxima sessão

- **WHEN** o personagem terminou a campanha/sessão anterior com `fate_current = 2` (tinha 3, gastou 1)
- **AND** inicia nova sessão
- **THEN** `fortune_current` e `fortune_max` SHALL ser `2`

#### Scenario: Sessão pausada retomada preserva Fortuna intra-sessão

- **WHEN** o jogador retoma sessão pausada existente
- **THEN** o sistema SHALL NOT recalcular Fortuna a partir de Destino
- **AND** SHALL manter `fortune_current`/`fortune_max` persistidos

---

### Requirement: FORT-03 — Fortuna intra-sessão não persiste entre sessões

Pontos de Fortuna gastos durante uma sessão SHALL permanecer gastos até o fim dessa sessão. Na próxima sessão nova, Fortuna SHALL ser restaurada conforme FORT-02.

#### Scenario: Fortuna parcialmente gasta na sessão

- **WHEN** o personagem inicia sessão com 3 Fortuna e gasta 1 em re-roll
- **THEN** `fortune_current` SHALL ser `2` até o fim da sessão
- **AND** na próxima sessão nova SHALL voltar a `fate_current` (ex.: 3 se nenhum Destino foi gasto)
