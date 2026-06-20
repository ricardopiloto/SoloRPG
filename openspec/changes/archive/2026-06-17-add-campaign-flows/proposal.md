# Change: Fluxos completos de campanha e personagem

## Why

Faltam na UI: criação customizada de personagem, retomar campanha ativa, escolha personagem existente vs novo ao iniciar campanha, marcar campanha concluída, tela de progressão completa.

## What Changes

- UI de criação customizada WFRP4e
- Botão "Continuar campanha" para campanhas ativas
- Fluxo pós-morte/conclusão: manter personagem ou novo
- API `POST /campaigns/{id}/complete`
- Tela de progressão com lista de avanços disponíveis (skills/talents)

## Impact

- Affected specs: `campaign-management`, `character-management`, `web-interface`
- Affected code: `routes.py`, `campaign.py`, `page.tsx`, novos componentes
