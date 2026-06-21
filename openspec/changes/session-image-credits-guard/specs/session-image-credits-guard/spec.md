# Spec: session-image-credits-guard

**Capability:** Validação de créditos no início da sessão e desligamento automático mid-session

---

## ADDED Requirements

### Requirement: IMG-CRED-01 — Probe no início de sessão nova

Nova sessão SHALL executar geração real de validação na Cloudflare antes do primeiro turno. O probe SHALL usar prompt fixo de validação e descartar os bytes gerados.

#### Scenario: Probe bem-sucedido habilita imagens

- **WHEN** uma nova sessão é criada e as credenciais Cloudflare estão válidas
- **AND** `probe_image_credits()` retorna sucesso
- **THEN** `GameSession.images_enabled` SHALL ser `true`
- **AND** sinais `[IMAGEM]` subsequentes MAY enfileirar jobs normalmente

#### Scenario: Probe falho desabilita imagens na sessão

- **WHEN** uma nova sessão é criada e o probe falha por qualquer motivo
- **THEN** `GameSession.images_enabled` SHALL permanecer `false`
- **AND** nenhuma imagem SHALL ser gerada durante toda a sessão

#### Scenario: Credenciais ausentes falham sem chamar API externa

- **WHEN** `CLOUDFLARE_ACCOUNT_ID` ou `CLOUDFLARE_API_TOKEN` não estão configurados
- **THEN** o probe SHALL falhar localmente sem requisição HTTP
- **AND** `images_enabled` SHALL ser `false`

#### Scenario: Sessão pausada retomada não re-probe

- **WHEN** o jogador retoma uma sessão pausada existente
- **THEN** o sistema SHALL reutilizar o valor persistido de `images_enabled`
- **AND** SHALL NOT executar novo probe de créditos

---

### Requirement: IMG-CRED-02 — Ignorar `[IMAGEM]` quando desabilitado

Quando `images_enabled=false`, o pipeline SHALL ignorar sinais `[IMAGEM]` silenciosamente.

#### Scenario: Sinal ignorado sem job

- **WHEN** o GM emite `[IMAGEM]` e `session.images_enabled` é `false`
- **THEN** nenhum `ImageJob` SHALL ser criado
- **AND** nenhum placeholder ou spinner SHALL aparecer no frontend
- **AND** a narrativa textual SHALL continuar normalmente

#### Scenario: Cache hit continua quando habilitado

- **WHEN** `images_enabled` é `true` e existe cache hit para a cena
- **THEN** o sistema MAY servir imagem em cache sem nova geração

---

### Requirement: IMG-CRED-03 — Desligamento mid-session por quota

Quando um job falha por quota ou créditos esgotados, a sessão SHALL desabilitar novas gerações de imagem.

#### Scenario: Quota esgotada desliga sessão

- **WHEN** um job de imagem falha com HTTP 429, código JSON `10000`, ou erro tipado equivalente de quota
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

---

### Requirement: IMG-CRED-04 — API expõe flag de sessão

Respostas de sessão SHALL incluir o estado de geração de imagens.

#### Scenario: SessionOut inclui images_enabled

- **WHEN** o cliente consulta `GET /sessions` ou detalhe de sessão
- **THEN** `SessionOut` e `SessionDetailOut` SHALL incluir `images_enabled: boolean`
- **AND** o valor SHALL refletir o estado persistido em `GameSession`
