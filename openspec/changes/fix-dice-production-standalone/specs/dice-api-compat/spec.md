# Spec: dice-api-compat

**Change:** `fix-dice-production-standalone`  
**Capability:** `dice-ui` (modificada)

---

## MODIFIED Requirements

### Requirement: DiceBox.clear() MUST ser chamado defensivamente

O helper `safeClear` em `diceBoxHost.ts` MUST testar se o retorno de `box.clear()` possui o método `.catch` antes de chamá-lo, evitando `TypeError` quando a implementação retorna `void`.

#### Scenario: clear() retorna Promise (dice-box ≥ 1.1.0 padrão)

- **Dado** que `box.clear()` retorna uma Promise
- **Quando** `safeClear(box)` é chamado
- **Então** `.catch(() => undefined)` é encadeado sobre a Promise
- **E** nenhum TypeError é lançado

#### Scenario: clear() retorna void (comportamento observado em produção)

- **Dado** que `box.clear()` retorna `void` (undefined)
- **Quando** `safeClear(box)` é chamado
- **Então** a checagem `typeof r?.catch === 'function'` é falsa
- **E** nenhuma tentativa de chamar `.catch` é feita
- **E** nenhum TypeError é lançado

#### Scenario: Sequência de rolls sem TypeError

- **Dado** que o usuário completa uma rolagem e o overlay fecha
- **Quando** o overlay fecha e `safeClear` é chamado na cleanup
- **Então** o singleton `initPromise` permanece válido
- **E** a próxima rolagem usa o mesmo DiceBox sem reinicialização

---

### Requirement: Indicador visual SHALL ser exibido quando DiceBox não inicializa

Quando `ensureDiceBox` retorna `null`, o `DiceOverlay` SHALL exibir mensagem informando que a animação 3D não está disponível e o resultado é numérico.

#### Scenario: DiceBox indisponível (WASM falha)

- **Dado** que `ensureDiceBox` retornou `null` (init falhou)
- **Quando** o overlay fica visível
- **Então** a mensagem "Dados físicos indisponíveis — resultado numérico" é exibida
- **E** um resultado numérico aleatório é emitido após `HOLD_MS`
- **E** nenhum spinner "Preparando dados…" fica preso indefinidamente

#### Scenario: DiceBox disponível (caminho feliz)

- **Dado** que `ensureDiceBox` retornou uma instância válida
- **Quando** o overlay fica visível
- **Então** o spinner "Preparando dados…" é exibido enquanto o roll processa
- **E** os dados 3D aparecem no canvas
- **E** resultado é determinístico (valor do motor físico)
