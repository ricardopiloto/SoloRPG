# Proposal: add-fate-fortune-mechanics

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `add-wfrp-solo-mvp` (implementação parcial de Fate/Fortune), `archive/2026-06-17-complete-memory-identity` (Fortune spend básico)

---

## Why

O MVP já persiste `fate_current`/`fortune_current`, mas as regras WFRP4e pedidas pelo jogador não estão completas nem alinhadas: Fortuna é campo independente na criação de personagem, não reinicia por sessão, permite efeito `+10` além de re-roll, e a UI exibe só Pontos de Destino. Precisamos formalizar Destino e Fortuna como recursos acoplados — Fortuna derivada do Destino vigente — com comportamentos distintos e permanentes vs. por sessão.

## What Changes

- **Ponto de Destino (Fate):** gastável para **evitar receber um ferimento** ou **sobreviver a golpe mortal**; o personagem sobrevive de alguma forma narrativa. **Nunca recupera** entre sessões ou campanhas.
- **Ponto de Fortuna (Fortune):** gastável para **re-rolar um teste mal-sucedido** (único efeito). **Reinicia no início de cada nova sessão** com valor igual aos **Pontos de Destino atuais** (`fate_current`) do personagem no momento do start — ex.: 3 Destino → 3 Fortuna; 2 Destino → 2 Fortuna.
- **Acoplamento Destino ↔ Fortuna:** remover `fortune_max` independente na criação; `fortune_max`/`fortune_current` derivados de `fate_current` ao iniciar sessão.
- **Sessão:** `start_session()` restaura `fortune_current = fate_current` e `fortune_max = fate_current`.
- **Re-roll com Fortuna:** fluxo de teste pendente permite gastar Fortuna para nova rolagem; deduz 1 Fortuna server-side.
- **UI:** sidebar exibe Destino e Fortuna separadamente (gemas ◆/◇ para ambos).
- **GM prompt:** instruções claras sobre quando emitir `usar_ponto_destino` vs. `usar_ponto_fortuna` (efeito `reroll` apenas).
- **Remover** efeito legado `bonus_teste` (+10) de Fortuna.

## Capabilities

### New Capabilities

- `fate-fortune-mechanics`: Regras completas de gasto, acoplamento e refresh por sessão de Destino e Fortuna.

### Modified Capabilities

- `wfrp-rules-engine`: Requisitos de Fate/Fortune atualizados — Destino evita ferimento/morte; Fortuna só re-roll; refresh por sessão.
- `session-orchestration`: Refresh de Fortuna em `start_session`.
- `web-interface`: Exibição dual Destino + Fortuna na sidebar e prompt de gasto em testes.
- `character-management`: Remover Fortuna independente na criação; derivar de Destino.

## Impact

| Área | Alterações |
|------|------------|
| Backend | `rules/fate.py`, `session.py`, `gm_orchestrator.py`, `character.py`, schemas API |
| Frontend | `CharacterSidebar.tsx`, `FateGems.tsx` (ou componente Fortune), fluxo de teste/`TestBlock` |
| GM | `gm-system-prompt.md`, contexto XML de memória |
| Testes | `test_rules.py`, `test_phase2_game_loop.py`, novos casos de refresh e re-roll |
