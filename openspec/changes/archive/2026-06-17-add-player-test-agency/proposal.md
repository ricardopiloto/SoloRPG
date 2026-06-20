# Change: Agência do jogador nos testes (Rolar dado)

## Why

O product-brief v1.1 §6 define que testes são momentos de agência: o GM apresenta opções, o jogador escolhe rolar via botão **"Rolar dado"**, a animação d100 ocorre, e só então o GM narra. Hoje o backend rola automaticamente no mesmo request — violando o fluxo especificado.

## What Changes

- Dois estágios no turno: (1) GM emite `[TESTE]` → UI mostra card de teste + botão; (2) jogador confirma → backend rola → GM narra consequência
- Endpoint `POST /api/sessions/{id}/roll` para execução do teste pendente
- Estado `pending_test` na sessão entre estágios
- UI: card destacado com atributo, alvo, modificador, botão "Rolar dado"
- GM narra consequência somente após resultado visível

## Impact

- Affected specs: `wfrp-rules-engine`, `synthetic-gm`, `web-interface`
- Affected code: `gm_orchestrator.py`, `session.py`, `routes.py`, `page.tsx`, novo componente `TestPromptCard.tsx`
