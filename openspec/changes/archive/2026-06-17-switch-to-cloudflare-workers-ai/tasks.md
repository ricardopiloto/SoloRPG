# Tasks: switch-to-cloudflare-workers-ai

## 1. Backend — cliente Cloudflare

- [x] 1.1 Criar `cloudflare_workers_ai.py` com POST para `@cf/black-forest-labs/flux-1-schnell`
- [x] 1.2 Adicionar `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_AI_MODEL` em `config.py`
- [x] 1.3 Remover `FLUX_API_KEY` / `FLUX_API_URL` de config e `.env.example`
- [x] 1.4 Implementar decode base64 → `generated_images/{job_id}.jpg`
- [x] 1.5 Adicionar `GET /api/images/{job_id}/file` para servir JPEG
- [x] 1.6 Atualizar `images.py` para usar novo client (manter cache, vínculos mapa/item)
- [x] 1.7 Remover `flux_client.py`

## 2. Testes

- [x] 2.1 Atualizar `test_images.py` com mock Cloudflare API
- [x] 2.2 Testar gravação de arquivo e URL `/file`
- [x] 2.3 Testar fallback sem credenciais (placeholder)
- [x] 2.4 Rodar suite completa: `pytest tests/ -q`

## 3. Documentação

- [x] 3.1 Atualizar `README.md` e `.env.example` (vars Cloudflare)
- [x] 3.2 Atualizar `openspec/project.md` (Tech Stack / External Dependencies)
- [x] 3.3 Alinhar `Docs/product-brief.md` §7.4 (provider Cloudflare)
- [x] 3.4 Alinhar `Docs/frontend-backend-split.md` tabela de integrações
- [x] 3.5 Marcar `add-flux-visual-pipeline` como superseded pelo provider em nota de `development-order.md`
- [x] 3.6 Adicionar `generated_images/` ao `.gitignore`

## 4. Validação

- [x] 4.1 Teste manual: turno com `[IMAGEM]` → placeholder → imagem inline no chat
- [x] 4.2 Teste manual: `tipo mapa` atualiza `MapRegion.image_url`
- [x] 4.3 Teste manual: `tipo item` aparece thumbnail no inventário
- [x] 4.4 Build frontend sem alterações: `npm run build`
