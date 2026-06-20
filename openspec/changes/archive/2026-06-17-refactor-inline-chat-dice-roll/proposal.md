# Proposal: refactor-inline-chat-dice-roll

## Why

A rolagem de dados 3D atual usa um overlay `position: fixed` que cobre toda a viewport (`Dice3DOverlay` como irmão de `ChatLog` em `/play/[sessionId]`). Isso diverge do protótipo Open Design (`dice-roll.html` + `js/dice.mjs`), onde a animação acontece **inline dentro da área de chat** — o jogador vê os dados rolando no centro do log de conversa, não num modal sobre toda a tela.

O protótipo já implementa o padrão correto via `DiceRoller.rollInChat()`: insere um bloco `.chat-roll-entry` no `#chat-log`, monta o canvas 3D num `.dice-canvas-host` com altura fixa (~280px), exibe label/meta do teste, mostra resultado com veredito e faz fade-out após `holdMs`. A configuração de física (`offscreen: false`, `themeColor: #C9973A`, `scale: 9.4`) e o ciclo de vida (`preload → roll → settle → fade → remove`) estão validados no showcase.

## What Changes

- **Substituir** o overlay fixo `Dice3DOverlay` por um componente inline `ChatRollEntry` renderizado **dentro** de `.chat-log` (`ChatLog`).
- **Portar** a lógica de `dice.mjs` para um módulo React (`lib/dice/diceRoller.ts` + hook `useDiceRoller`) mantendo o carregamento estático de `@3d-dice/dice-box` via `webpackIgnore`.
- **Reposicionar** o mount point do canvas 3D para a região scrollável do chat (`section.chat-column > div.chat-log`), com dimensões explícitas (min-height ~280px, width 100%).
- **Adaptar** `useSessionPlay` para inserir uma entrada `kind: "dice-roll"` no array de `ChatEntry` em vez de togglear `diceVisible` num overlay externo.
- **Remover** CSS de overlay fullscreen (`.dice-3d-container { position: fixed }`) e adicionar estilos inline espelhando `dice.css` do protótipo (`.chat-roll-entry`, `.dice-stage`, `.dice-result-block`).
- **Manter** fallback 2D (`prefers-reduced-motion`, WebGL indisponível) dentro do mesmo bloco inline.
- **Atualizar** `Docs/ux-spec.md` §4–§5 para refletir posicionamento inline no chat-log (não `position: fixed`).

## Impact

- **Affected specs:** `dice-ui`, `game-chat-ux` (posicionamento da animação)
- **Affected code:**
  - `frontend/src/components/session/ChatLog.tsx`
  - `frontend/src/components/dice/Dice3DOverlay.tsx` → removido/substituído
  - `frontend/src/components/dice/3d/DiceBoxWrapper.tsx` → refatorado para mount inline
  - `frontend/src/hooks/useSessionPlay.ts`
  - `frontend/src/app/play/[sessionId]/page.tsx`
  - `frontend/src/app/globals.css`
- **Breaking:** nenhum breaking de API backend; apenas mudança de UX frontend.
- **Dependencies:** builds sobre `fix-dice-box-v11-api` (carregamento estático do dice-box) — não conflita, complementa.

## Out of Scope

- Rolagem de tipos além de d100 na sessão (d10 de dano/iniciativa) — o showcase do protótipo suporta, mas a sessão MVP usa d100; tipos extras ficam para change futuro.
- Som de impacto dos dados (já especificado em `add-3d-dice`, não implementado).
- Forçar resultado visual do backend no dice-box (`value` predeterminado) — dice-box não suporta; animação decorativa + resultado do cliente permanece.
