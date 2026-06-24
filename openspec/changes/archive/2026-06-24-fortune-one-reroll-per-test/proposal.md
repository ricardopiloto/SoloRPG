# Proposal: fortune-one-reroll-per-test

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `add-fate-fortune-mechanics` (re-roll com Fortuna em teste falho)

---

## Why

Hoje, após falhar um teste GM, o jogador pode gastar Fortuna para re-rolar — e se falhar de novo, a UI ainda oferece novo re-roll enquanto houver Pontos de Fortuna. Nas regras WFRP pedidas, **cada teste permite no máximo um re-roll com Fortuna**: falhou → re-rolou uma vez → resultado final, mesmo que ainda restem Fortunas na sessão.

## What Changes

- **Limite por teste:** flag `fortune_reroll_used` no estado do teste pendente (`pending_roll_result`); inicia `false` na primeira rolagem e vira `true` após um re-roll com Fortuna.
- **Backend:** `execute_fortune_reroll()` rejeita se `fortune_reroll_used=true`; `RollResponse` expõe `fortune_reroll_available` para a UI.
- **Frontend:** prompt "Gastar Fortuna" só aparece quando `failed && fortune_current > 0 && !fortune_reroll_used`.
- **Novo teste GM:** reset da flag quando GM emite novo `[TESTE]`.

## Capabilities

### New Capabilities

_(nenhuma — delta em capability existente)_

### Modified Capabilities

- `fate-fortune-mechanics`: Fortuna permite no máximo 1 re-roll por instância de teste GM.
- `web-interface`: UI não oferece segundo re-roll no mesmo teste.

## Impact

| Área | Alterações |
|------|------------|
| Backend | `gm_orchestrator.py` (`execute_roll`, `execute_fortune_reroll`), `schemas/api.py`, `routes.py` |
| Frontend | `useSessionPlay.ts`, `play/[sessionId]/page.tsx` |
| Testes | `test_fate_fortune_mechanics.py` + caso de segundo re-roll bloqueado |
