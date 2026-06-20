# Tasks: Fidelidade total às animações do Dice So Nice (via @3d-dice/dice-box)

## 1. Instalar package e copiar assets

- [x] 1.1 Instalar: `cd frontend && npm install @3d-dice/dice-box`
- [x] 1.2 Criar diretório: `mkdir -p frontend/public/assets/dice-box`
- [x] 1.3 Copiar todos os assets do package para `public/`:
  ```bash
  cp -r frontend/node_modules/@3d-dice/dice-box/dist/* frontend/public/assets/dice-box/
  ```
- [x] 1.4 Confirmar que os seguintes arquivos existem em `public/assets/dice-box/`:
  - `assets/themes/default/default.json`, `diffuse-dark.png`, `diffuse-light.png`, `normal.png`, `specular.jpg`, `theme.config.json`
  - `assets/ammo/ammo.wasm.wasm`
  - `world.offscreen.js`, `world.onscreen.js`, `Dice.js`
- [x] 1.5 Adicionar ao `.gitignore`:
  ```
  frontend/public/assets/dice-box/
  ```

## 2. Criar componente `DiceBoxWrapper.tsx`

- [x] 2.1 Criar `frontend/src/components/dice/3d/DiceBoxWrapper.tsx` com config BabylonJS
- [x] 2.2 Lógica de rolagem: `box.roll("2d10")` + `onRollComplete` reporta valor do servidor
- [x] 2.3 Cleanup no unmount: `box.clear()`
- [x] 2.4 Estado de loading: spinner "carregando dados..." enquanto `init()` não completa

## 3. Criar declarações TypeScript para o package

- [x] 3.0 Criar `frontend/src/types/dice-box.d.ts` com tipos para `@3d-dice/dice-box` (package sem `.d.ts`)

## 4. Atualizar `Dice3DOverlay.tsx`

- [x] 4.1 Substituir `Dice3DCanvas` por `DiceBoxWrapper` via `next/dynamic` com `ssr: false`
- [x] 4.2 Remover estados `settled`, `tens`, `units`; usar `resultRoll` como resultado do servidor
- [x] 4.3 `handleSettled(serverRoll)` exibe overlay com valor do servidor
- [x] 4.4 Manter detecção de `prefers-reduced-motion` e `useWebGLSupported` com fallback `DiceOverlay2D`

## 5. Remover implementação anterior

- [x] 5.1 Remover `frontend/src/components/dice/3d/dice3d-geometry.ts`
- [x] 5.2 Remover `frontend/src/components/dice/3d/DicePhysics.ts`
- [x] 5.3 Remover `frontend/src/components/dice/3d/Dice3DCanvas.tsx`
- [x] 5.4 Remover `frontend/src/components/dice/3d/DiceSounds.ts`
- [x] 5.5 Confirmar sem imports orphan: nenhuma referência encontrada nos fontes

## 6. CSS e layout

- [x] 6.1 Remover `.dice-3d-canvas` obsoleto do `globals.css`
- [x] 6.2 Adicionar regra para canvas BabylonJS injetado: `#dice-canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none }`
- [x] 6.3 Manter `.dice-3d-result`, `.dice-3d-values`, `.dice-3d-total`, `.dice-3d-die-label`

## 7. Build e validação

- [x] 7.1 `npm run build` — build limpo, sem erros de TypeScript
- [x] 7.2 Confirmar que `public/assets/dice-box/` está no `.gitignore`
- [ ] 7.3 Teste visual local: rolar dado → animação BabylonJS roda, overlay exibe resultado correto
- [ ] 7.4 Testar `prefers-reduced-motion` → exibir `DiceOverlay2D`
