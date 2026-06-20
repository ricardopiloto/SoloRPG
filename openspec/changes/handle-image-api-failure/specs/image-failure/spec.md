# Spec: image-failure

**Capability:** Tratativa silenciosa de falha na geração de imagens

---

## MODIFIED Requirements

### Requirement: IMG-FAIL-01 — Falha na API de imagens MUST ser transparente ao usuário

Quando a API de geração de imagens (Cloudflare Workers AI) falhar por qualquer motivo — indisponibilidade, timeout, erro HTTP, API não configurada — o chat MUST continuar sem exibir nenhum elemento visual relacionado à imagem. Nenhum placeholder, nenhum spinner eterno, nenhuma mensagem de erro MUST aparecer no chat.

O backend SHALL registrar a falha em log (`WARNING`) para fins de diagnóstico sem expô-la ao usuário.

#### Scenario: Tokens/quota da API esgotados (HTTP 429)

**Dado** que a conta CF Workers AI atingiu o limite de tokens ou requisições  
**Quando** a CF retorna HTTP 429 para o job de imagem  
**Então** `CloudflareGenerationError` SHALL ser lançado com mensagem identificando "quota/tokens esgotados"  
**E** `ImageJob.status` SHALL ser `"failed"` e `ImageJob.image_url` SHALL ser `null`  
**E** o log SHALL conter `WARNING` com o tipo de erro e status 429 para diagnóstico operacional  
**E** o frontend MUST NOT renderizar nenhum elemento visual para esse job

#### Scenario: Quota sinalizada via JSON (HTTP 200 + success:false)

**Dado** que a CF retorna HTTP 200 com `{"success": false, "errors": [...]}` indicando quota excedida  
**Quando** o JSON é processado em `generate_image`  
**Então** `CloudflareGenerationError` SHALL ser lançado com os erros da resposta  
**E** `ImageJob.status` SHALL ser `"failed"` e `ImageJob.image_url` SHALL ser `null`

#### Scenario: API retorna erro HTTP (503, 502, 5xx)

**Dado** que a CF Workers AI retorna um status HTTP de erro de servidor  
**Quando** o job de imagem é processado em background  
**Então** `ImageJob.status` SHALL ser `"failed"` e `ImageJob.image_url` SHALL ser `null`  
**E** o frontend MUST NOT renderizar nenhum elemento visual para esse job  
**E** `document` MUST NOT conter nenhum `<figure>` ou `<img>` relacionado ao job falho

#### Scenario: Timeout de rede

**Dado** que a requisição à CF Workers AI excede o timeout de `httpx`  
**Quando** `httpx.TimeoutException` é lançado  
**Então** `ImageJob.status` SHALL ser `"failed"` e `ImageJob.image_url` SHALL ser `null`  
**E** o job MUST NOT permanecer em `"processing"` indefinidamente

#### Scenario: API não configurada (chaves ausentes)

**Dado** que `CLOUDFLARE_ACCOUNT_ID` ou `CLOUDFLARE_API_TOKEN` não estão definidos  
**Quando** o backend tenta processar um job de imagem  
**Então** `ImageJob.status` SHALL ser `"failed"` e `ImageJob.image_url` SHALL ser `null`  
**E** nenhum placeholder MUST aparecer no chat do usuário

#### Scenario: Imagem já falha na resposta do turno

**Dado** que o backend retorna `TurnResponse` com `images: [{status: "failed", ...}]`  
**Quando** o frontend processa `appendImages`  
**Então** a entrada de imagem MUST NOT ser adicionada à lista de `entries` do chat  
**E** nenhum spinner ou elemento visual MUST ser exibido

---

### Requirement: IMG-FAIL-02 — Fluxo feliz MUST continuar inalterado

Quando a API de geração de imagens funciona corretamente, o comportamento atual MUST ser preservado sem regressão.

#### Scenario: Geração bem-sucedida

**Dado** que a CF Workers AI está disponível e retorna imagem válida  
**Quando** o job é processado  
**Então** `ImageJob.status` SHALL ser `"completed"` e `ImageJob.image_url` SHALL ser a URL do arquivo gerado  
**E** o `SceneImage` MUST exibir a imagem no chat após o polling detectar `status="completed"`

---

## Cross-references

- `add-flux-visual-pipeline` — implementou o pipeline original
- `switch-to-cloudflare-workers-ai` — migrou para CF Workers AI
- `add-game-chat-ux` — `SceneImage` introduzido aqui
