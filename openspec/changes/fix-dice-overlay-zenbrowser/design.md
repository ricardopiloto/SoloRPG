# Design: fix-dice-overlay-zenbrowser

## Diagnóstico

```
visible=true → roll effect → diceBoxRef.current === null → throw "not ready"
```

| Causa | Evidência | Fix |
|-------|-----------|-----|
| Race init vs roll | Roll no primeiro clique antes de `init()` | `await ensureDiceBox()` |
| Canvas 0×0 no init | `postMessage({ width: clientWidth })` com 0 | `waitForContainerSize()` |
| Assets 404 | `public/assets/dice-box/` gitignored | `npm run prepare:dice` |
| Zen/Firefox workers | Blob worker fallback já no dice-box | `origin` explícito + assets locais |

## Decisions

### 1. Singleton `ensureDiceBox(containerSelector)`

- Uma instância por sessão de play
- Init idempotente via promise compartilhada
- Re-init se container mudar de tamanho de 0 para >0 (primeira vez)

### 2. Roll enfileirado

Quando `visible` sobe:
```typescript
const box = await ensureDiceBox(`#${STAGE_ID}`);
await box.roll("1d100");
```

Se init falhou → fallback RNG (comportamento existente).

### 3. Config inalterada (biblioteca)

```typescript
{
  assetPath: "/assets/dice-box/assets/",
  container: `#${STAGE_ID}`,
  offscreen: false,
  origin: window.location.origin,
  // ... física WFRP existente
}
```

### 4. Assets via script, não commit

`.gitignore` mantém binários fora do repo; `prepare:dice` roda após `npm install`.

## Risks

| Risco | Mitigação |
|-------|-----------|
| Init lento no primeiro roll | Preload no mount + mensagem "Preparando dados…" |
| Zen bloqueia WebGL | dice-box cai em `world.none.js`; fallback RNG |
