# session-lifecycle Specification

## Purpose
TBD - created by archiving change add-session-pause-resume. Update Purpose after archive.
## Requirements
### Requirement: Pausa de sessão ativa
O sistema SHALL permitir ao jogador pausar uma sessão de jogo ativa antes que ela seja encerrada definitivamente, congelando o timer e preservando todo o estado da sessão no banco de dados.

#### Scenario: Pausa bem-sucedida
- **WHEN** o jogador chama `POST /sessions/{id}/pause` com sessão `is_active=True` e `paused_at=null`
- **THEN** a sessão recebe `paused_at = datetime.now(utc)`, o timer é congelado nesse instante e a resposta retorna `SessionDetail` atualizado com `paused_at != null`

#### Scenario: Tentativa de pausar sessão já pausada
- **WHEN** o jogador chama `POST /sessions/{id}/pause` com `paused_at` já definido
- **THEN** o sistema retorna HTTP 400 com mensagem de erro indicando que a sessão já está pausada

#### Scenario: Tentativa de pausar sessão encerrada
- **WHEN** o jogador chama `POST /sessions/{id}/pause` com `is_active=False`
- **THEN** o sistema retorna HTTP 404 ou HTTP 400 com mensagem de sessão inativa

---

### Requirement: Retomada de sessão pausada
O sistema SHALL permitir ao jogador retomar uma sessão pausada, descongelando o timer a partir do ponto em que foi pausado e disponibilizando o histórico de chat completo para exibição no frontend.

#### Scenario: Retomada bem-sucedida
- **WHEN** o jogador chama `POST /sessions/{id}/resume` com `paused_at != null`
- **THEN** o sistema calcula `delta = now - paused_at`, incrementa `total_paused_seconds += delta`, zera `paused_at = null`, persiste e retorna `SessionDetail` com `paused_at = null`

#### Scenario: Tempo restante ajustado após pausa
- **WHEN** o jogador pausa por 10 minutos e retoma
- **THEN** `session_time_remaining_minutes()` retorna o mesmo valor de antes da pausa (±1 min de arredondamento), confirmando que os 10 minutos de pausa foram descontados do elapsed

#### Scenario: Tentativa de retomar sessão não pausada
- **WHEN** o jogador chama `POST /sessions/{id}/resume` com `paused_at=null`
- **THEN** o sistema retorna HTTP 400 com mensagem de que a sessão não está pausada

---

### Requirement: Proteção contra sessão duplicada
O sistema SHALL retornar a sessão pausada existente quando o jogador tenta iniciar uma nova sessão para uma campanha que já possui uma sessão pausada.

#### Scenario: Start com sessão pausada existente retorna a existente
- **WHEN** o jogador chama `POST /campaigns/{id}/sessions` e existe `GameSession` com `campaign_id = id`, `is_active = True` e `paused_at != null`
- **THEN** o sistema retorna a sessão pausada existente com HTTP 200 (sem criar nova sessão)

#### Scenario: Start com sessão ativa não-pausada ainda levanta erro
- **WHEN** o jogador chama `POST /campaigns/{id}/sessions` e existe `GameSession` com `is_active = True` e `paused_at = null`
- **THEN** o sistema retorna HTTP 400 com "Já existe uma sessão ativa"

---

### Requirement: Histórico de chat persistido e restaurável
O sistema SHALL expor um endpoint que retorna todos os turnos de uma sessão em ordem cronológica, permitindo ao frontend reconstruir o histórico visual de chat após uma pausa.

#### Scenario: Histórico retornado em ordem
- **WHEN** o jogador chama `GET /sessions/{id}/history`
- **THEN** o sistema retorna lista de `SessionTurnOut` com `role`, `content`, `metadata` e `created_at`, ordenada por `created_at ASC`

#### Scenario: Histórico vazio para sessão nova
- **WHEN** o jogador chama `GET /sessions/{id}/history` para sessão recém-criada sem turns
- **THEN** o sistema retorna lista vazia `[]` com HTTP 200

---

### Requirement: Timer com desconto de pausa
O sistema SHALL calcular o tempo restante de sessão descontando o total de segundos em que a sessão esteve pausada, usando a fórmula:

```
time_remaining_seconds = duration_minutes * 60
                         - (now - started_at).total_seconds()
                         + total_paused_seconds
```

#### Scenario: Timer congelado durante pausa
- **WHEN** a sessão está com `paused_at != null`
- **THEN** chamadas sucessivas a `session_time_remaining_minutes()` retornam o mesmo valor (o tempo não decrementa enquanto pausado)

#### Scenario: Timer retoma corretamente após pausa longa
- **WHEN** a sessão é pausada por 30 minutos e retomada em uma sessão de 45 min com 20 min decorridos antes da pausa
- **THEN** após a retomada o tempo restante é ~25 min (45 - 20), não ~(-5) min

---

### Requirement: Exibição de sessão pausada na tela de campanhas
O frontend SHALL indicar visualmente sessões pausadas na listagem de campanhas e oferecer ação de "Retomar" em vez de "Iniciar sessão".

#### Scenario: Badge de sessão pausada
- **WHEN** a campanha possui sessão com `paused_at != null`
- **THEN** o card da campanha exibe badge "Pausada" e o tempo restante congelado

#### Scenario: Botão "Retomar" navega para a sessão correta
- **WHEN** o jogador clica em "Retomar"
- **THEN** o frontend navega para `/play/{sessionId}` da sessão pausada, que automaticamente chama `POST /resume` e carrega o histórico via `GET /sessions/{id}/history`

---

### Requirement: Botão de pausa na interface de jogo
O frontend SHALL disponibilizar um botão "Pausar sessão" na tela de jogo que, ao ser acionado, pausa a sessão e redireciona o jogador para a tela de campanhas.

#### Scenario: Pausa desabilitada durante ação em andamento
- **WHEN** `loading=true` ou `diceVisible=true`
- **THEN** o botão "Pausar sessão" está desabilitado, prevenindo pausa durante streaming de narrativa ou animação de dados

#### Scenario: Pausa bem-sucedida via UI
- **WHEN** o jogador clica em "Pausar sessão" com jogo em estado normal (`loading=false`, `diceVisible=false`)
- **THEN** o frontend chama `POST /sessions/{id}/pause`, exibe feedback de confirmação e navega para `/campaigns`

