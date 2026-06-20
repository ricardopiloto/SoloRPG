# Proposal: fix-silent-api-failures

**Data:** 2026-06-20  
**Status:** Draft  
**Escopo:** `frontend/src/app/` (home, campaigns, character) · `backend/app/rules/careers.py` (estabilidade)

---

## Problema

Após a change `update-character-sidebar-stats-ui`, usuários reportam que o site "não faz nada":
- Nova campanha não responde ao clique
- Criação de personagem não funciona
- Histórico e campanhas em andamento não aparecem

## Causa raiz

Combinação de **regressão backend transitória** + **falta de feedback no frontend**:

1. **Backend:** Durante hot reload, `careers.py` ficou momentaneamente sem `XP_MAX` / `SKILL_ADVANCE_COST`, quebrando importações. Logs mostram também `sqlite3.OperationalError: no such table: campaigns` em estado de DB inconsistente.

2. **Frontend:** Páginas `home`, `campaigns` e `character` usam `Promise.all(...).then(...)` **sem `.catch()`**. Quando a API retorna 500, o estado permanece `[]`, erros só aparecem no console, e ações como `newCampaign()` retornam cedo (`if (!selectedChar) return`) — parecendo "clique morto".

## Solução

- Adicionar tratamento de erro visível (`error` state + mensagem) em home, campaigns e character
- `try/catch` em ações de criação (pregen, custom, nova campanha) com mensagem ao usuário
- Garantir `careers.py` estável (constantes XP intactas após refactor de skills)
- Backend startup já executa `create_all` — documentar reinício do uvicorn após erros de schema

## Não-escopo

- Refatorar camada `api.ts` globalmente
- Migrar banco de dados existente
