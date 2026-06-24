# Tasks: fix-chat-scroll-containment

## 1. Scroll explícito no container ChatLog

- [x] 1.1 Adicionar `containerRef = useRef<HTMLDivElement>(null)` em `ChatLog.tsx` e vincular ao `<div className="chat-log">`
- [x] 1.2 Substituir scroll inicial por `containerRef.current.scrollTop = containerRef.current.scrollHeight`
- [x] 1.3 Substituir scroll de nova mensagem por `containerRef.current.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" })`
- [x] 1.4 Dado inline: skip de scroll enquanto `diceActive === true` (DiceOverlay cobre tudo — scroll desnecessário)
- [x] 1.5 Remover `bottomRef` e sentinel desnecessários; simplificar `useEffect`

## 2. Reforço de contenção no layout da sessão

- [x] 2.1 `.game-shell { h-dvh overflow-hidden }` — confirmado em `globals.css:66`
- [x] 2.2 `.chat-column { min-h-0 overflow-hidden }` — confirmado em `globals.css:93`
- [x] 2.3 `DiceOverlay` renderiza `#wfrp-dice-stage`, backdrop e UI com `position: absolute inset-0` relativo a `.chat-column` (irmãos do `.chat-log`) — confirmado em `DiceOverlay.tsx`
- [x] 2.4 `SessionPrepareOverlay` usa `position: fixed inset-0` — confirmado em `SessionPrepareOverlay.tsx:13`

## 3. Validação

- [ ] 3.1 Dev: abrir `/play/[sessionId]`, enviar 10+ mensagens e confirmar que apenas `.chat-log` scrolla (`document.scrollingElement.scrollTop === 0` no DevTools)
- [ ] 3.2 Confirmar que `div.chat-log` tem `getBoundingClientRect().top >= 0` (nunca negativo)
- [ ] 3.3 **`chat-input-area` fixo:** confirmar visualmente que o input permanece no rodapé durante e após o auto-scroll
- [ ] 3.4 **Dado — visual:** acionar uma rolagem; confirmar que o DiceOverlay cobre toda a `.chat-column` sem artefatos
- [ ] 3.5 **Dado — após rolagem:** confirmar que o chat e o input estão em posição correta após `onDone`
- [x] 3.6 `npm run build` — ✓ zero erros TypeScript
- [ ] 3.7 Abrir `/character`, `/campaigns` — confirmar que scroll nessas páginas não regrediu
