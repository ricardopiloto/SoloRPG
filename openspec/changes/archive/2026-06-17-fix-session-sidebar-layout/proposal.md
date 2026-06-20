# Change: Painéis laterais fixos na tela de sessão

## Why

Na tela de sessão ativa, os painéis laterais (ficha/inventário à esquerda, mapa/diário à direita) rolam junto com a página ou com o conteúdo central. Isso quebra a imersão — o jogador perde referência da ficha e do mapa enquanto lê a narrativa longa no chat.

## What Changes

- Painéis esquerdo e direito permanecem fixos na viewport durante a sessão
- Apenas a área central (histórico do chat) possui scroll vertical
- Header da sessão e input de texto permanecem fixos na coluna central
- Painéis laterais podem ter scroll interno independente se o conteúdo exceder a altura da tela
- Layout responsivo: em telas estreitas (< lg), painéis empilham sem quebrar a regra de scroll isolado do chat

## Impact

- Affected specs: `web-interface` (MODIFIED — Session Layout)
- Affected code: `frontend/src/app/page.tsx`, possivelmente `frontend/src/components/SidePanels.tsx`, `frontend/src/components/CharacterSheet.tsx`
- Sem impacto em backend ou APIs
