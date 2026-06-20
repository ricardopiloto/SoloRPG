# Tasks: refactor-inline-chat-dice-roll

## 1. Módulo dice roller (port do protótipo)

- [x] 1.1 Criar `frontend/src/lib/dice/diceRoller.ts` portando de `dice.mjs`: `loadDiceBox`, `ensureDiceBox`, `rollPhysics`, `formatD100`, `calcSL`, config WFRP
- [x] 1.2 Criar `frontend/src/hooks/useDiceRoller.ts` com singleton, `preload()`, `rollInline(containerSelector, opts)`, cleanup
- [x] 1.3 Garantir carregamento via `webpackIgnore` de `/assets/dice-box/dice-box.es.min.js` (reutilizar padrão de `DiceBoxWrapper`)

## 2. Componente inline no chat

- [x] 2.1 Criar `frontend/src/components/dice/ChatRollEntry.tsx` com estrutura DOM do protótipo (label, meta, stage, canvas-host, result-block)
- [x] 2.2 Adicionar CSS em `globals.css`: `.chat-roll-entry`, `.dice-inline-stage`, `.dice-canvas-host`, `.dice-result-block`, estados `.is-rolling`, `.is-done`, `.is-fading-out`, `.dice-canvas-hidden`
- [x] 2.3 Implementar ciclo: loading → roll → result → holdMs (2000) → fade (400ms) → onComplete(roll)

## 3. Integração com ChatLog

- [x] 3.1 Estender `ChatEntry` com `kind: "dice-roll"` (label, meta, target?, onComplete callback via ref/context)
- [x] 3.2 Renderizar `<ChatRollEntry />` em `ChatLog` para entradas `dice-roll`
- [x] 3.3 Auto-scroll suave para a entrada de rolagem ao inserir (sem re-scroll durante animação)

## 4. Integração com sessão

- [x] 4.1 Refatorar `useSessionPlay.rollTest()` para append `dice-roll` entry em vez de `setDiceVisible(true)`
- [x] 4.2 Refatorar `useSessionPlay.quickRoll()` com mesmo padrão (label/meta do quick roll)
- [x] 4.3 Manter `onDiceDone(roll)` como callback pós-animação; remover prop `diceVisible`/`diceRoll` expostos desnecessariamente
- [x] 4.4 Remover `<Dice3DOverlay />` de `play/[sessionId]/page.tsx`
- [x] 4.5 Chamar `preload()` no mount da página de sessão

## 5. Fallback e acessibilidade

- [x] 5.1 Fallback 2D inline quando `prefers-reduced-motion` ou WebGL indisponível (mesmo bloco, sem canvas 3D)
- [x] 5.2 ARIA: `aria-live="assertive"` no bloco de rolagem; resultado sempre em texto

## 6. Limpeza

- [x] 6.1 Remover ou deprecar `Dice3DOverlay.tsx` e CSS `.dice-3d-container { position: fixed }`
- [x] 6.2 Refatorar `DiceBoxWrapper.tsx` — lógica absorvida por `diceRoller.ts` / `ChatRollEntry`

## 7. Documentação e validação

- [x] 7.1 Atualizar `Docs/ux-spec.md` §4–§5: posicionamento inline no `.chat-log`, não overlay fixed
- [x] 7.2 Atualizar `Docs/prototype-gap-analysis.md` §9: inline chat roll alinhado ao protótipo
- [x] 7.3 `npm run build` sem erros TypeScript
- [x] 7.4 Teste manual: rolar teste solicitado → dados visíveis no centro do chat-log → fade → narrativa GM
- [x] 7.5 Teste manual: quick roll da sidebar → mesmo comportamento inline
