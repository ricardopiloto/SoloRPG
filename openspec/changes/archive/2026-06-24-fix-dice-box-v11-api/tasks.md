# Tasks: Alinhamento ao API v1.1 do @3d-dice/dice-box

## 1. Corrigir die notation para `"1d100"`

- [x] 1.1 Em `DiceBoxWrapper.tsx`, substituir `box.roll("2d10")` por `box.roll("1d100")` em todos os locais (init pending roll + roll effect)

## 2. Corrigir construtor para API v1.1

- [x] 2.1 Em `DiceBoxWrapper.tsx`, substituir `new DiceBox("#id", {...})` por `new DiceBox({ container: "#dice-canvas-mount-point", ... })`
- [x] 2.2 Callbacks `onRollComplete` mantidos por closure em cada `roll()` call para capturar `serverRoll` corretamente — sem race condition

## 3. Corrigir tipo TypeScript

- [x] 3.1 `frontend/src/types/dice-box.d.ts` atualizado: construtor `(config: DiceBoxConfig)` com `container?: string | HTMLElement`
- [x] 3.2 Tipos completos adicionados: `DieResult`, `RollResultGroup`, todos os callbacks, `RollResultGroup[]` em `onRollComplete`

## 4. Implementar dismiss com `hide()` e CSS fade

- [x] 4.1 `DiceBoxWrapper.tsx`: `roll === null` agora chama `box.hide("dice-hide")` + `setTimeout 300ms` + `box.clear()`
- [x] 4.2 `globals.css`: `.dice-hide { opacity: 0 !important; transition: opacity 0.3s ease-out; }`

## 5. Ajustar `themeColor`

- [x] 5.1 `themeColor: "#1a120b"` → `"#2e1a0a"` (marrom couro escuro, mais visível)

## 6. Build e validação

- [x] 6.1 `npm run build` — build limpo, sem erros TypeScript
- [ ] 6.2 Confirmar que o console do browser **não** exibe "You are using the old API" ao inicializar
- [ ] 6.3 Teste visual: rolar dado → animação `d100` aparece, overlay fecha com fade, resultado correto exibido
