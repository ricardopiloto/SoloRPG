# Spec: dice-wasm-load

**Change:** `fix-dice-production-standalone`  
**Capability:** nova — `dice-wasm-load`

---

## ADDED Requirements

### Requirement: WASM MUST ser servido com Content-Type correto em produção

O Caddyfile do servidor MUST incluir uma regra explícita que force `Content-Type: application/wasm` para qualquer request cujo path termine em `.wasm`.

#### Scenario: Request para ammo.wasm retorna MIME correto

- **Dado** que o Caddy está configurado com a regra `@wasm { path *.wasm }`
- **Quando** o browser faz GET para `/assets/dice-box/assets/ammo/ammo.wasm`
- **Então** a resposta tem header `Content-Type: application/wasm`
- **E** o browser não rejeita o arquivo como tipo desconhecido

#### Scenario: Assets que não são WASM não são afetados

- **Dado** que a regra `@wasm` só aplica a paths `*.wasm`
- **Quando** o browser faz GET para qualquer outro asset (`.js`, `.glb`, etc.)
- **Então** o Content-Type não é alterado pela regra `@wasm`

---

### Requirement: Headers COOP/COEP MUST estar presentes para isolamento de processo

O bloco do domínio `solorpg.1nodado.com.br` no Caddyfile MUST incluir os headers `Cross-Origin-Opener-Policy` e `Cross-Origin-Embedder-Policy` necessários para que Workers e SharedArrayBuffer funcionem.

#### Scenario: Headers presentes em todas as respostas do frontend

- **Dado** que o Caddyfile tem `header Cross-Origin-Opener-Policy "same-origin"` e `header Cross-Origin-Embedder-Policy "require-corp"`
- **Quando** qualquer página do frontend é carregada
- **Então** os headers estão presentes nas respostas HTTP do Caddy
- **E** o DiceBox pode inicializar Workers sem bloqueio do browser

#### Scenario: COOP/COEP não quebra outras funcionalidades

- **Dado** que os headers COOP/COEP estão ativos
- **Quando** o usuário navega para login, chat, e inventário
- **Então** todas as rotas funcionam sem erros de isolamento de origem

---

### Requirement: Build Docker MUST incluir smoke check de assets WASM

O `frontend/Dockerfile` MUST verificar a existência do arquivo `public/assets/dice-box/assets/ammo/ammo.wasm` após executar `prepare:dice`, falhando o build se o arquivo estiver ausente.

#### Scenario: Build bem-sucedido com assets presentes

- **Dado** que `npm run prepare:dice` copiou os assets corretamente
- **Quando** o Docker executa o smoke check `RUN ls public/assets/dice-box/assets/ammo/ammo.wasm`
- **Então** o build continua normalmente

#### Scenario: Build falha se assets ausentes

- **Dado** que `prepare:dice` falhou silenciosamente (ex: `node_modules` ausente)
- **Quando** o Docker executa o smoke check
- **Então** o comando retorna exit code não-zero
- **E** o build Docker falha com mensagem clara antes de gerar imagem defeituosa
