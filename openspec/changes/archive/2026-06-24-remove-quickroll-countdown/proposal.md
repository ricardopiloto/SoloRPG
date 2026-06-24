# Proposal: remove-quickroll-countdown

**Data:** 2026-06-23  
**Status:** Draft  
**Arquivo afetado:** `frontend/src/components/character/QuickRollPopover.tsx` (único)

---

## Why

Ao clicar em uma perícia ou atributo na sidebar para rolar, o `QuickRollPopover` exibe um countdown regressivo de 2 segundos e **auto-executa o roll** ao final. Esse comportamento:

- Surpresa o jogador que clicou por acidente ou que queria ajustar o modificador antes
- Não dá tempo para cancelar quando o clique foi involuntário
- A mensagem "Rolando em 2s…" é confusa — parece que algo está travado
- O botão "Rolar agora" já existe e cobre o caso de quem quer rolar imediatamente

A solução é remover o countdown e deixar o popover como uma interface **sempre explícita**: o jogador decide quando rolar.

---

## What Changes

Em `QuickRollPopover.tsx`:

1. Remover o estado `countdown` e o `useEffect` que decrementar o timer e dispara `onRoll` automaticamente
2. Remover a mensagem `"Rolando em {countdown}s…"` do JSX
3. Manter tudo o mais: botão "Rolar agora", botão "Cancelar", controles de modificador (+/−)

O popover continua aparecendo na mesma posição com a mesma interação — apenas sem o timer automático.

---

## Capabilities

### Modified Capabilities

- **quickroll-ux**: popover de rolagem rápida deixa de ter auto-roll por timer

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/components/character/QuickRollPopover.tsx` | Remove countdown state, useEffect e texto "Rolando em Xs…" |

---

## Non-Goals

- Alterar o comportamento da rolagem em si (API, resultado, narração)
- Mudar posição ou visual do popover
- Remover o botão "Rolar agora" ou o campo de modificador
