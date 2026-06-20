# Change: Quick roll na sidebar de personagem

## Why

`Docs/ux-spec.md` §6 e o protótipo `game.html` permitem rolagens rápidas clicando em atributos, perícias ou armas na sidebar esquerda, com popover de modificador e countdown de 2s. O frontend atual não tem essa interação; rolagens só ocorrem via testes do GM.

## What Changes

- Sidebar: atributos, perícias e armas clicáveis (classe `rollable`)
- Popover `quick-roll` com título, alvo, modificador ±, "Rolar agora" / "Cancelar", countdown 2s
- Endpoint backend `POST /session/{id}/quick-roll` com validação server-side
- Resultado exibido via `DiceOverlay` + mensagem de sistema no chat (`roll-system-msg`)
- Integração com `add-frontend-prototype-parity` (CharacterSidebar)

## Impact

- Affected specs: `web-interface`, `wfrp-rules-engine`
- Affected code: `frontend/src/components/character/`, `backend/app/api/routes/session.py`, rules engine roll helper
- Dependências: `add-frontend-prototype-parity` (layout sessão), Fase 1 (DB + backend rodando)

## Out of Scope

- Rolagens durante testes GM (coberto por `add-player-test-agency`)
- `@3d-dice/dice-box` — reutiliza DiceOverlay CSS do protótipo
