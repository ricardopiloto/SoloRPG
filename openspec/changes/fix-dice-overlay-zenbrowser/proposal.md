# Proposal: fix-dice-overlay-zenbrowser

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `add-3d-dice`, `fix-dice-box-v11-api`, `@3d-dice/dice-box` ^1.1.4

---

## Why

No macOS com Zen Browser (Firefox-based), a rolagem 3D falha com `[DiceOverlay] roll failed: Error: not ready`. O `diceBoxRef` está `null` no momento do roll — causado por (1) **race condition**: o jogador rola antes de `box.init()` terminar; (2) **init com canvas 0×0**: física AmmoJS recebe dimensões zero se o container ainda não layoutou; (3) **assets ausentes**: `/public/assets/dice-box/` é gitignored e pode não existir após clone; (4) **falha silenciosa**: init falha no catch mas o roll tenta mesmo assim.

## What Changes

- **Módulo `diceBoxHost`**: singleton com promise de init, espera por dimensões do container, retry e estado `ready | failed`.
- **`DiceOverlay`**: aguarda init antes de `roll()`; exibe loading até pronto; fallback RNG se init falhar.
- **CSS**: `#wfrp-dice-stage` com dimensões mínimas explícitas para init estável.
- **Script `prepare:dice`**: copia assets de `node_modules/@3d-dice/dice-box/dist/` para `public/assets/dice-box/`.
- **Sem trocar biblioteca**: mantém `@3d-dice/dice-box` e carregamento estático via `webpackIgnore`.

## Capabilities

### Modified Capabilities

- `dice-ui`: init robusto e roll sincronizado com readiness do DiceBox.

## Impact

| Área | Alterações |
|------|------------|
| Frontend | `lib/dice/diceBoxHost.ts`, `DiceOverlay.tsx`, `globals.css`, `package.json` |
| Docs | README — passo `npm run prepare:dice` após install |
