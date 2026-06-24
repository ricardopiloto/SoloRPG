# signal-alignment Specification

## Purpose
TBD - created by archiving change sync-gm-prompt-v23. Update Purpose after archive.
## Requirements
### Requirement: apply_nova_campanha lê ponto_de_partida

O backend SHALL ler o campo `ponto_de_partida` do payload `[NOVA_CAMPANHA]` e gravá-lo em `campaign.world_state`. Quando o campo estiver ausente, SHALL usar `gancho_inicial` como fallback para retrocompatibilidade com campanhas anteriores.

#### Scenario: Campanha criada com ponto_de_partida v2.3

- **Dado** que o LLM emite `[NOVA_CAMPANHA]` com `"ponto_de_partida": "Você acaba de chegar em Ubersreik e percebe que alguém te seguiu pela última légua"`
- **Quando** `apply_nova_campanha` processa o payload
- **Então** `campaign.world_state` SHALL conter o valor de `ponto_de_partida`
- **E** o contexto injetado ao GM na próxima sessão SHALL incluir `<estado_do_mundo>Você acaba de chegar...</estado_do_mundo>`

#### Scenario: Retrocompatibilidade com gancho_inicial legado

- **Dado** que um payload antigo usa `"gancho_inicial": "O personagem acorda sem memória"`
- **Quando** `apply_nova_campanha` processa o payload
- **Então** `campaign.world_state` SHALL conter o valor de `gancho_inicial`

---

### Requirement: apply_nova_campanha persiste ganchos_ocultos

O backend SHALL ler o campo `ganchos_ocultos` do payload `[NOVA_CAMPANHA]` e gravá-lo em `campaign.campaign_summary` como um bloco estruturado, preservando os ganchos para referência em sessões futuras.

#### Scenario: Ganchos ocultos gravados na abertura da campanha

- **Dado** que o LLM emite `[NOVA_CAMPANHA]` com `"ganchos_ocultos": ["A cicatriz do ferreiro é nova demais", "O cão da guarda não latiu", "Um rosto conhecido na multidão fugiu ao ser visto"]`
- **Quando** `apply_nova_campanha` processa o payload
- **Então** `campaign.campaign_summary` SHALL conter as três strings de gancho precedidas de marcador `[GANCHOS OCULTOS]`
- **E** o campo SHALL ser persistido no banco antes do retorno da função

#### Scenario: Payload sem ganchos_ocultos não afeta campaign_summary

- **Dado** que o payload `[NOVA_CAMPANHA]` não contém o campo `ganchos_ocultos`
- **Quando** `apply_nova_campanha` processa o payload
- **Então** `campaign.campaign_summary` SHALL permanecer `None` (sem modificação)

---

### Requirement: _handle_combat_state persiste status de inimigos por turno

O backend SHALL ler o campo `inimigos` do payload `[ESTADO_COMBATE]` no formato v2.3 e atualizar o `status` de cada combatente correspondente em `session.combat_state`. O campo SHALL ser identificado por `nome` e o `status` atualizado in-place.

#### Scenario: Status de inimigo atualizado após turno

- **Dado** que `session.combat_state` contém `{"combatants": [{"nome": "Salteador", "tipo": "npc", "status": "normal"}]}`
- **E** o LLM emite `[ESTADO_COMBATE]` com `"inimigos": [{"nome": "Salteador", "status": "ferido"}]`
- **Quando** `_handle_combat_state` processa o payload
- **Então** `session.combat_state["combatants"][0]["status"]` SHALL ser `"ferido"`
- **E** a mudança SHALL ser persistida via `await db.commit()`

#### Scenario: Inimigo não encontrado no combat_state não causa erro

- **Dado** que `session.combat_state` não contém um combatente com nome "Arqueiro fantasma"
- **E** o payload traz `"inimigos": [{"nome": "Arqueiro fantasma", "status": "morto"}]`
- **Quando** `_handle_combat_state` processa o payload
- **Então** o backend SHALL ignorar silenciosamente o inimigo não encontrado (sem exceção)

---

### Requirement: _handle_combat_state persiste proxima_acao

O backend SHALL ler o campo `proxima_acao` do payload `[ESTADO_COMBATE]` e gravá-lo em `session.combat_state["proxima_acao"]` para que o frontend possa indicar visualmente de quem é o turno.

#### Scenario: proxima_acao gravada corretamente

- **Dado** que o payload `[ESTADO_COMBATE]` contém `"proxima_acao": "personagem"`
- **Quando** `_handle_combat_state` processa o payload
- **Então** `session.combat_state["proxima_acao"]` SHALL ser `"personagem"`

---

### Requirement: TestBlock exibe opcao_alternativa para testes opcionais

O componente `TestBlock` SHALL exibir o texto de `opcao_alternativa` quando o campo estiver presente e `obrigatorio` for `false` (ou ausente), dando ao jogador visibilidade sobre a ação alternativa disponível sem precisar reler a narrativa.

O botão "Rolar dado" SHALL ser exibido independentemente do valor de `obrigatorio` — conforme o GM System Prompt v2.4: "A obrigatoriedade é do teste, não da rolagem. O jogador vê o componente de dado e rola normalmente — a rolagem é sempre dele."

#### Scenario: Alternativa visível em teste opcional com obrigatorio false

- **Dado** que o `pending.payload` contém `{ "obrigatorio": false, "opcao_alternativa": "Recuar pelo beco" }`
- **Quando** `TestBlock` é renderizado
- **Então** o componente SHALL exibir o texto "Recuar pelo beco" em estilo itálico abaixo do botão de rolar
- **E** SHALL exibir um label diferenciador como "Ou:" antes do texto alternativo
- **E** o botão "Rolar dado" SHALL estar presente e habilitado

#### Scenario: Alternativa oculta em teste obrigatório — rolagem sempre disponível

- **Dado** que o `pending.payload` contém `{ "obrigatorio": true, "opcao_alternativa": null }`
- **Quando** `TestBlock` é renderizado
- **Então** o componente SHALL NOT exibir nenhuma seção de alternativa
- **E** o botão "Rolar dado" SHALL estar presente e habilitado (o jogador sempre rola)

#### Scenario: obrigatorio ausente trata como false

- **Dado** que o `pending.payload` não contém o campo `obrigatorio`
- **Quando** `TestBlock` é renderizado
- **Então** o componente SHALL tratar como `obrigatorio: false` e exibir `opcao_alternativa` se presente

---

### Requirement: TestBlock distingue testes obrigatórios de opcionais

O componente `TestBlock` SHALL exibir títulos distintos para testes obrigatórios (`obrigatorio: true`) e opcionais (`obrigatorio: false` ou ausente), refletindo a diferença narrativa definida no GM System Prompt v2.4: obrigatório significa que o jogador não pode pular o teste, não que o sistema rola automaticamente.

#### Scenario: Título "Teste obrigatório" para situações automáticas

- **Dado** que o `pending.payload` contém `{ "obrigatorio": true }`
- **Quando** `TestBlock` é renderizado
- **Então** o label superior SHALL exibir "Teste obrigatório" (em vez de "Teste solicitado")

#### Scenario: Título "Teste solicitado" para testes por escolha

- **Dado** que o `pending.payload` contém `{ "obrigatorio": false }`
- **Quando** `TestBlock` é renderizado
- **Então** o label superior SHALL exibir "Teste solicitado"

