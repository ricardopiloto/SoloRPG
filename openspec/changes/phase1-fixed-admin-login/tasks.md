# Tasks: phase1-fixed-admin-login

## 1. Config e seed

- [x] 1.1 `AUTH_MODE` (`fixed_admin` | `multi_user`) e `ADMIN_PASSWORD` em `config.py`
- [x] 1.2 `validate_startup`: `ADMIN_PASSWORD` ≥8 em `fixed_admin`; SMTP só em `multi_user` + production
- [x] 1.3 `services/admin_user.py` — `ensure_admin_user()` (substitui `dev_master.py`)
- [x] 1.4 Lifespan chama `ensure_admin_user` quando `fixed_admin`
- [x] 1.5 Documentar em `.env.example` e README

## 2. Backend auth

- [x] 2.1 `authenticate_user` — branch `fixed_admin`: admin + ADMIN_PASSWORD
- [x] 2.2 Normalizar login: `admin` → `admin@wfrp-solo.local`
- [x] 2.3 Guard `require_multi_user_auth` em register/verify/resend → 404
- [x] 2.4 `GET /auth/config` → `{ auth_mode, login_username }`
- [x] 2.5 Remover/desativar `dev_master.py` e alias `dev`

## 3. Testes backend

- [x] 3.1 `test_admin_login.py` — login ok, senha errada, register 404
- [x] 3.2 Atualizar `conftest.py` — `ADMIN_PASSWORD` no env de teste; helper `admin_login()`
- [x] 3.3 Testes multi_user existentes: monkeypatch `AUTH_MODE=multi_user` onde necessário
- [x] 3.4 `pytest` verde

## 4. Frontend

- [x] 4.1 Consumir `GET /auth/config` ou env para modo fixed_admin
- [x] 4.2 `/login` — só senha em fixed_admin; remover link register
- [x] 4.3 `/register` e `/verify-email` → redirect `/login` em fixed_admin
- [x] 4.4 Remover hint/prefill dev/dev
- [x] 4.5 i18n `auth.passwordOnly`, atualizar strings

## 5. E2E e integração

- [x] 5.1 `game-loop.spec.ts` — login admin + ADMIN_PASSWORD
- [x] 5.2 `playwright.config.ts` — `ADMIN_PASSWORD` no backend test env

## 6. Documentação

- [x] 6.1 README — login fixo fase 1, sem cadastro/SMTP
- [x] 6.2 `Docs/debian-server-install.md` — remover SMTP; adicionar ADMIN_PASSWORD
- [x] 6.3 `Docs/mvp-validation-checklist.md` — login admin
- [x] 6.4 Nota em `add-auth-dev-bypass/proposal.md` — superseded
- [x] 6.5 Atualizar `phase1-controlled-release-readiness/proposal.md` — escopo conta única

## 7. Validação manual

- [x] 7.1 Subir app → login admin + senha do .env → home com starter
- [x] 7.2 `/register` inacessível; API register → 404
- [x] 7.3 Deploy staging: trocar ADMIN_PASSWORD sem recriar DB (hash atualizado no startup)
