# Design: Rolagem inline no chat-log

## Context

O protótipo Open Design (`dice.mjs`) separa dois modos:

| Modo | Função | Container |
|------|--------|-----------|
| Theater | `DiceRoller.roll()` | `#dice-canvas-host` num modal fullscreen |
| **Inline (sessão)** | `DiceRoller.rollInChat()` | `.dice-canvas-host` dentro de `.chat-roll-entry` no `#chat-log` |

O usuário pediu explicitamente o modo inline, com a área de rolagem limitada ao DOM path:

```
div.game-shell > div.game-body > section.chat-column > div.chat-log
```

Componente React alvo: `ChatLog`.

## Decisions

### 1. Entrada de chat dedicada (`kind: "dice-roll"`)

Em vez de overlay externo, `useSessionPlay` adiciona ao array `entries`:

```typescript
{
  kind: "dice-roll",
  label: "Teste de Agilidade",
  meta: "Ag 38 + Percepção +4 · Alvo 42",
  target?: number,
  onComplete: (roll: number) => void,
}
```

`ChatLog` renderiza `<ChatRollEntry />` para essa entrada. Ao completar, a entrada é removida (fade-out) e o fluxo existente (`onDiceDone` → API) continua.

**Alternativa rejeitada:** manter `Dice3DOverlay` como portal renderizado dentro de `.chat-log` via `createPortal`. Funciona, mas mistura estado externo com DOM interno; a entrada no array de chat é mais coerente com auto-scroll e histórico visual.

### 2. Singleton DiceBox com remount de container

O protótipo reutiliza uma instância global `diceBox` e troca `activeContainer` quando o seletor muda (`ensureDiceBox(containerSelector)`). No React:

- Hook `useDiceRoller` mantém instância singleton (module-level ou contexto na rota `/play`).
- Cada `ChatRollEntry` registra seu `#dice-canvas-host-{id}` como container ativo ao montar.
- Ao desmontar (fade-out), chama `box.clear()` + `box.hide('dice-canvas-hidden')`.

**Config alinhada ao protótipo:**

```javascript
{
  assetPath: '/assets/dice-box/assets/',
  themeColor: '#C9973A',
  background: 'transparent',
  scale: 9.4,
  gravity: 2.2,
  mass: 1.4,
  friction: 0.85,
  restitution: 0.25,
  spinForce: 6,
  throwForce: 7,
  startingHeight: 10,
  settleTimeout: 6000,
  offscreen: false,  // canvas onscreen dentro do chat-log — dimensões explícitas
}
```

`offscreen: false` é crítico: o canvas precisa de dimensões reais do `.dice-canvas-host` (~280px altura). Com `offscreen: true` + container sem tamanho definido, o canvas pode renderizar invisível (bug reportado).

### 3. Carregamento estático (webpackIgnore)

Manter a abordagem de `DiceBoxWrapper` atual:

```typescript
await import(/* webpackIgnore: true */ '/assets/dice-box/dice-box.es.min.js')
```

Workers (`world.onscreen.js`, `world.offscreen.js`) e WASM (`ammo.wasm`) devem resolver relativamente a `/assets/dice-box/`.

### 4. Layout e CSS

Estrutura DOM (espelhando protótipo):

```html
<div class="chat-roll-entry is-rolling">
  <div class="chat-roll-label">Teste de Agilidade</div>
  <div class="chat-roll-meta">Ag 38 + Percepção +4 · Alvo 42</div>
  <div class="dice-inline-stage">
    <div class="dice-canvas-host" id="dice-canvas-host-{uuid}"></div>
    <div class="dice-stage-loading">Preparando dados 3D…</div>
  </div>
  <div class="dice-result-block">
    <div class="dice-result-total"></div>
    <div class="dice-result-verdict"></div>
  </div>
</div>
```

CSS (portar de `dice.css` + tokens WFRP):

- `.chat-roll-entry`: `max-width: 65ch`, `margin: 28px auto`, centralizado no chat-log
- `.dice-inline-stage`: `min-height: 280px`, `position: relative`, fundo escuro, borda accent
- `.dice-canvas-host`: `width: 100%`, `height: 280px`
- `.dice-result-block.is-visible`: fade-in do resultado
- `.chat-roll-entry.is-fading-out`: opacity transition antes de remover do DOM

**Sem** `position: fixed` nem backdrop blur sobre toda a tela. O chat continua visível acima e abaixo do bloco de dados.

### 5. Fluxo de rolagem (teste solicitado)

```
[Jogador clica "Rolar dado" no TestBlock]
  → useSessionPlay.rollTest()
  → append ChatEntry { kind: "dice-roll", label, meta, target }
  → ChatLog auto-scroll para a nova entrada
  → ChatRollEntry monta → useDiceRoller.roll({ container, type: "d100" })
  → Animação 3D no canvas inline (~3–6s)
  → onRollComplete → exibe resultado + veredito (sucesso/falha vs target)
  → holdMs 2000 → fade-out → remove entrada
  → onComplete(roll) → useSessionPlay.onDiceDone(roll) → API rollTest + narrate
```

Quick roll segue o mesmo padrão com label/meta diferentes.

### 6. Fallback 2D inline

Se WebGL indisponível ou `prefers-reduced-motion`:

- `.dice-inline-stage` recebe classe `.is-fallback`
- Animação CSS simples (d10 wobble do protótipo) ou contador numérico
- Mesmo bloco de resultado e fade-out

### 7. Preload

Chamar `useDiceRoller.preload()` no mount de `/play/[sessionId]` (equivalente a `DiceRoller.preload()` no protótipo) para reduzir delay no primeiro roll.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Canvas 0×0 se host não tiver altura | Altura fixa 280px no CSS; `offscreen: false` |
| Múltiplos rolls simultâneos | Bloquear UI durante roll (`diceVisible` → derivado de entry `dice-roll` ativa) |
| Scroll jump durante animação | Auto-scroll apenas na inserção; não re-scroll durante física |
| Singleton DiceBox leak entre sessões | Cleanup no unmount da rota `/play` |

## Migration

1. Implementar `ChatRollEntry` + `useDiceRoller` em paralelo
2. Trocar `rollTest`/`quickRoll` para usar entrada inline
3. Remover `Dice3DOverlay` de `page.tsx` e CSS fixed overlay
4. Validar visualmente contra protótipo `dice-roll.html`
