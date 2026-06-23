# Tasks: phase1-controlled-release-readiness

Legenda: `[dep]` = depende de apply de outra change.

---

## Track A — Fechar escopo fase 1 (pregens only)

- [ ] A.1 Verificar código `limit-chargen-to-pregen-phase1` vs spec; marcar tasks 1.x–3.x como `[x]` em `limit-chargen-to-pregen-phase1/tasks.md`
- [ ] A.2 Atualizar README § "Criação de personagem" — remover referência à aba wizard; descrever starter + pregens
- [ ] A.3 Atualizar README § "Loop de Jogo" item 1 — "starter ou pré-gerado", não customizado
- [ ] A.4 Confirmar home CTA `home.anotherCharacter` → `/character` (pregens) — task 4.2 limit-chargen

## Track B — Dev bypass `[dep: add-auth-dev-bypass]`

- [ ] B.1 Aplicar `add-auth-dev-bypass` completo (config, routes, frontend, testes)
- [ ] B.2 Documentar fluxo dev one-click vs prod verify no README

## Track C — Produção e segurança

- [ ] C.1 Implementar `APP_ENV` + `is_production` (se não feito em B.1)
- [ ] C.2 Startup fail-fast: prod + JWT default → erro; prod + `EMAIL_PROVIDER!=smtp` → erro
- [ ] C.3 Criar `Docs/phase1-release-runbook.md` — template env Vercel + Railway/Supabase
- [ ] C.4 Documentar `CORS_ORIGINS` com URL real do frontend deployado
- [ ] C.5 (Opcional P2) Rate limit básico em `POST /auth/register` e `/auth/login`

## Track D — Testes automatizados

- [ ] D.1 Atualizar `frontend/e2e/game-loop.spec.ts` — auth antes do loop (dev login ou register+verify mock)
- [ ] D.2 Atualizar `playwright.config.ts` — `JWT_SECRET`, `EMAIL_PROVIDER`, `APP_ENV` no webServer backend
- [ ] D.3 Decidir gate `test_images.py`: corrigir ou excluir de `run-tests.sh` com nota
- [ ] D.4 `RUN_E2E=1 ./scripts/run-tests.sh` verde

## Track E — Validação manual (sign-off)

- [ ] E.1 `add-user-auth` 9.1 — cadastro → verify (mock/SMTP) → home com starter
- [ ] E.2 `add-user-auth` 9.2 — login pós-verify; unverified bloqueado em prod
- [ ] E.3 `add-user-auth` 9.3 — segunda conta não vê personagens da primeira
- [ ] E.4 `/character` — só pregens; `curl` wizard → 403
- [ ] E.5 Atualizar `Docs/mvp-validation-checklist.md` — pré-requisito auth + remover "customizado"
- [ ] E.6 (Opcional) 1 sessão DeepSeek real em staging — checklist §Sessão 1

## Track F — Release

- [ ] F.1 Deploy staging (frontend + backend + Supabase)
- [ ] F.2 Smoke test staging com conta real (verify e-mail)
- [ ] F.3 Convidar grupo controlado (≤10) com runbook de onboarding
- [ ] F.4 Archive OpenSpec: `add-user-auth`, `limit-chargen-to-pregen-phase1`, `add-auth-dev-bypass`, esta change

---

## Resumo executivo — o que falta hoje

| # | Item | Track | Esforço |
|---|------|-------|---------|
| 1 | Dev bypass (`add-auth-dev-bypass`) | B | ~1 dia |
| 2 | Sync docs/tasks chargen | A | ~2 h |
| 3 | Guards produção (JWT, SMTP, APP_ENV) | C | ~3 h |
| 4 | E2E com auth | D | ~3 h |
| 5 | Validação manual auth | E | ~2 h |
| 6 | Deploy runbook + staging | C, F | ~0.5–1 dia |
| 7 | Fix/quarantine test_images | D | ~1 h (opcional) |

**Estimativa total até teste controlado:** 2–3 dias de trabalho focado.
