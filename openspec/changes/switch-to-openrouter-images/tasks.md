# Tasks: switch-to-openrouter-images

## Fase 1 — Cliente OpenRouter

- [x] **T1** Criar `backend/app/services/openrouter_images.py` com `OpenRouterImagesClient`, exceções, `probe_image_credits`, `is_quota_or_credit_error`
- [x] **T2** POST `https://openrouter.ai/api/v1/images` — payload `model`, `prompt`, `output_format: jpeg`, `aspect_ratio: 16:9`
- [x] **T3** Decodificar `data[0].b64_json`; wrap `httpx.HTTPStatusError` (402/429 → quota)
- [x] **T4** Preservar `WFRP_STYLE_PREFIX`, `COMPOSITION_HINTS`, probe prompt

## Fase 2 — Config e wiring

- [x] **T5** `config.py`: `openrouter_api_key`, `openrouter_image_model` (default Klein 4B); remover `cloudflare_*`
- [x] **T6** `images.py` + `session.py`: imports do novo módulo
- [x] **T7** Remover `cloudflare_workers_ai.py`
- [x] **T8** Atualizar `.env.example` e `.env.docker.example`

## Fase 3 — Testes

- [x] **T9** Adaptar `test_images.py` — mock OpenRouter JSON, chave via `OPENROUTER_API_KEY`
- [x] **T10** Adaptar `test_session_image_credits_guard.py` — probe + quota 402/429
- [x] **T11** Teste unitário cliente: decode base64, erro sem `data`, HTTP 402
- [x] **T12** `pytest backend/tests/test_images.py backend/tests/test_session_image_credits_guard.py`

## Fase 4 — Documentação

- [x] **T13** `CHANGELOG.md` (Unreleased) — breaking: migrar env vars
- [x] **T14** `Docs/architecture.md` + `Docs/debian-server-install.md` (troubleshooting imagens)
- [x] **T15** `openspec/project.md` — Tech Stack + External Dependencies
- [x] **T16** Spec deltas + `openspec validate switch-to-openrouter-images --strict`

## Fase 5 — Validação manual

- [ ] **T17** Nova sessão com chave válida → probe OK → `[IMAGEM]` cena aparece no chat
- [ ] **T18** Sem `OPENROUTER_API_KEY` → sessão sem imagens, narrativa normal
- [ ] **T19** Simular quota esgotada (402) → `images_enabled=false`, sem novos jobs

## Dependências

- T1–T4 antes de T6–T7
- T5 paralelo a T1
- T9–T11 após T1–T7
- T17–T19 após deploy local com chave real
