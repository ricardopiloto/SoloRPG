# Tasks: add-auth-dev-bypass

## 1. Config e startup

- [x] 1.1 `APP_ENV` em `config.py` + `is_production`; default inteligente com `DATABASE_PROFILE`
- [x] 1.2 Constantes master: `dev@localhost`, alias `dev`, senha `dev`
- [x] 1.3 `ensure_dev_master_user()` — user verificado + starter se ausente
- [x] 1.4 Chamar seed no `lifespan` após DB ready (somente development)
- [x] 1.5 Startup guards em production (JWT default, EMAIL_PROVIDER)
- [x] 1.6 Documentar `APP_ENV` + credenciais em `.env.example` e README

## 2. Login master

- [x] 2.1 `normalize_login_email()` — alias `dev` → `dev@localhost` em development
- [x] 2.2 Usar normalização em `authenticate_user` / `POST /auth/login`
- [x] 2.3 Confirmar register/verify **sem** bypass em dev

## 3. Testes backend

- [x] 3.1 `test_auth_dev_master.py` — login dev/dev e dev@localhost/dev → 200
- [x] 3.2 Prod: login dev/dev → 401; master user não existe
- [x] 3.3 Starter character presente após seed

## 4. Frontend

- [x] 4.1 `lib/env.ts` — `isDevAppEnv` (`NEXT_PUBLIC_APP_ENV`)
- [x] 4.2 `/login`: hint `auth.devMasterHint`; prefill opcional dev/dev
- [x] 4.3 i18n PT-BR

## 5. Documentação e alinhamento

- [x] 5.1 README — seção “Login de desenvolvimento (dev / dev)”
- [x] 5.2 Nota em `phase1-controlled-release-readiness`: substituir referência a `/auth/dev/login`

## 6. Validação manual

- [x] 6.1 Subir backend dev → login dev/dev na UI → home com starter
- [x] 6.2 `APP_ENV=production`: dev/dev falha; cadastro normal exige verify
