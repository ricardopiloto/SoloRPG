# Spec delta: session-image-credits-guard

**Change:** `switch-to-openrouter-images`

---

## MODIFIED Requirements

### Requirement: IMG-CRED-01 — Probe no início de sessão nova

Nova sessão SHALL executar geração real de validação via **OpenRouter Image API** antes do primeiro turno. O probe SHALL usar prompt fixo de validação (`PROBE_PROMPT`) com modelo configurado e descartar os bytes gerados.

#### Scenario: Probe bem-sucedido habilita imagens

- **WHEN** uma nova sessão é criada e `OPENROUTER_API_KEY` está válida
- **AND** `probe_image_credits()` retorna sucesso após `POST /api/v1/images`
- **THEN** `GameSession.images_enabled` SHALL ser `true`
- **AND** sinais `[IMAGEM]` subsequentes MAY enfileirar jobs normalmente

#### Scenario: Probe falho desabilita imagens na sessão

- **WHEN** uma nova sessão é criada e o probe falha por qualquer motivo
- **THEN** `GameSession.images_enabled` SHALL permanecer `false`
- **AND** nenhuma imagem SHALL ser gerada durante toda a sessão

#### Scenario: Credenciais ausentes falham sem chamar API externa

- **WHEN** `OPENROUTER_API_KEY` não está configurada
- **THEN** o probe SHALL falhar localmente sem requisição HTTP
- **AND** `images_enabled` SHALL ser `false`

#### Scenario: Sessão pausada retomada não re-probe

- **WHEN** o jogador retoma uma sessão pausada existente
- **THEN** o sistema SHALL reutilizar o valor persistido de `images_enabled`
- **AND** SHALL NOT executar novo probe de créditos

---

### Requirement: IMG-CRED-03 — Desligamento mid-session por quota

Quando um job falha por quota ou créditos esgotados na OpenRouter, a sessão SHALL desabilitar novas gerações de imagem.

#### Scenario: Quota esgotada desliga sessão

- **WHEN** um job de imagem falha com HTTP **402**, HTTP **429**, ou mensagem de erro tipada equivalente de quota/credits insuficientes
- **THEN** `GameSession.images_enabled` SHALL ser persistido como `false` imediatamente
- **AND** novos sinais `[IMAGEM]` SHALL NOT enfileirar jobs

#### Scenario: Erro transitório não desliga sessão

- **WHEN** um job falha por timeout, `ConnectError`, ou HTTP 503
- **THEN** o job SHALL falhar individualmente
- **AND** `images_enabled` SHALL permanecer inalterado
- **AND** sinais `[IMAGEM]` futuros MAY continuar enfileirando jobs

#### Scenario: Jobs enfileirados antes do desligamento

- **WHEN** `images_enabled` passa a `false` mid-session
- **THEN** jobs já enfileirados MAY completar ou falhar
- **AND** novos jobs SHALL NOT ser criados após o desligamento
