# Change: Alinhamento ao API v1.1 do @3d-dice/dice-box

## Why

A implementação atual (`upgrade-3d-dice-dsn-fidelity`) usa a **API v1.0 (antiga)** do `@3d-dice/dice-box` instalado na versão **1.1.4**. O código-fonte do package confirma isso:

```js
// dist/dice-box.es.js linha 161 (v1.1.4):
if (arguments.length === 2 && ...)
  console.warn("You are using the old API. Dicebox constructor accepts a config object
  as it's only argument. Please read the v1.1.0 docs at https://fantasticdice.games/docs/usage/config")
  l = arguments[1]; l.container = arguments[0]
```

| Problema | Atual (errado) | Correto (v1.1 API) |
|---|---|---|
| Construtor | `new DiceBox("#selector", {config})` | `new DiceBox({container: "#selector", ...config})` |
| Tipo TS | Construtor `(selector, config)` | Construtor `(config)` com `container` no objeto |
| Dado WFRP | `"2d10"` (2 dados separados) | `"1d100"` (dado percentual nativo, suportado como tipo de dado) |
| Callbacks | Atribuídos pós-`init()` | Podem ser passados no objeto de config |
| Dismiss | `clear()` imediato | `hide(className)` com CSS fade + `clear()` |
| `themeColor` | `#1a120b` (quase preto) | `#2e1a0a` (marrom couro mais legível) |

O erro original "You must provide a DOM selector as the first argument" ocorreu porque a versão anterior passava um `HTMLElement` (não um seletor string) como primeiro arg. A correção feita resolveu o crash, mas ainda usa a API velha. Esta proposta alinha tudo ao v1.1 oficial.

## What Changes

### 1. Construtor v1.1 — objeto único de config

Substitui `new DiceBox("#id", {...})` por `new DiceBox({ container: "#id", ...config })`.

### 2. Declarações TypeScript atualizadas

`frontend/src/types/dice-box.d.ts` corrige a assinatura do construtor para `(config: DiceBoxConfig)` com `container` como campo do objeto.

### 3. Die notation `"1d100"` — dado percentual correto

O `d100` é o dado percentual nativo do package (documentado em "Die Types"). Tecnicamente já representa os dois dados embutidos: dezenas (0–90) e unidades (0–9), da mesma forma que um dado percentual físico de RPG.

- **`"1d100"`**: 1 dado de 100 faces → retorna valor `1–100` → decomposto em dezenas + unidades para o overlay
- **`"2d10"` (descartado)**: 2 dados separados → menos fiel ao conceito de dado percentual único

**Decisão**: usar `"1d100"`. O `onRollComplete` retorna o valor do package (ignorado — usamos o valor do servidor). O overlay continua decompondo o `roll` do servidor em `tensDisplay` e `unitsDisplay` para exibição.

### 4. Callbacks no config

`onRollComplete` e `onDieComplete` podem ser passados no objeto de configuração inicial — mais limpo que atribuir `box.onRollComplete = fn` após `init()`. Com isso, não há risco de race condition se o callback for atribuído antes do evento disparar.

### 5. Dismiss com `hide()` + CSS fade

Ao fechar o overlay, usar `box.hide("dice-hide")` (adiciona uma classe CSS) para um fade-out suave antes de chamar `clear()`. A classe `dice-hide` define `opacity: 0; transition: opacity 0.3s ease-out`.

### 6. `themeColor` ajustado

`#1a120b` é quase preto e pode tornar o dado invisível em fundos escuros. Usar `#2e1a0a` (marrom couro escuro, mas visível).

## Impact

- Affected specs: `dice-ui`
- Files:
  - `frontend/src/components/dice/3d/DiceBoxWrapper.tsx` — novo construtor v1.1, callbacks no config, `hide()` no dismiss
  - `frontend/src/types/dice-box.d.ts` — assinatura corrigida
  - `frontend/src/app/globals.css` — adicionar `.dice-hide { opacity: 0; transition: opacity 0.3s ease-out }`
- No backend changes
- No asset changes (assets copiados em `upgrade-3d-dice-dsn-fidelity` permanecem)
