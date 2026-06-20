# Tasks: fix-silent-api-failures

## 1. Frontend — error handling

- [x] 1.1 `campaigns/page.tsx`: `.catch()` no load; mensagem de erro visível
- [x] 1.2 `page.tsx` (home): `.catch()` no load; mensagem de erro visível
- [x] 1.3 `character/page.tsx`: `.catch()` no load pregen; `try/catch` + erro em selectPregen/createCustom

## 2. Backend — verificação

- [x] 2.1 Confirmar `careers.py` com constantes XP intactas
- [x] 2.2 Smoke test: GET /characters, GET /campaigns, POST /characters/pregen, POST /campaigns

## 3. Validação

- [ ] 3.1 Simular API offline — UI mostra erro, não tela vazia silenciosa
- [ ] 3.2 Fluxo feliz: criar personagem → nova campanha → listagens populadas
