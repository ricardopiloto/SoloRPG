# Tasks: add-quick-roll-sidebar

## 1. Backend

- [x] 1.1 Criar `POST /session/{session_id}/quick-roll` com body `{ type, key, modifier }`
- [x] 1.2 Validar tipo (attribute/skill/weapon) e calcular alvo via rules engine
- [x] 1.3 Retornar `{ roll, target, success_levels, narration_hint }`
- [x] 1.4 Registrar rolagem no log da sessão

## 2. Frontend

- [x] 2.1 Marcar attrs/skills/weapons na sidebar como `rollable`
- [x] 2.2 Implementar `QuickRollPopover` (mod ±, countdown 2s, cancelar)
- [x] 2.3 Posicionar popover próximo ao item clicado
- [x] 2.4 Disparar `DiceOverlay` + `roll-system-msg` no chat após roll
- [x] 2.5 Desabilitar quick roll durante teste GM pendente

## 3. Validação

- [x] 3.1 Teste unitário rules engine para quick roll com modificador
- [x] 3.2 Teste manual: clicar Escalar (S) → popover → rolar → overlay
- [x] 3.3 Verificar timeout 2s auto-roll quando configurado no protótipo
