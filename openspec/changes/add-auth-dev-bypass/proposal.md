# Proposal: add-auth-dev-bypass

**Data:** 2026-06-22  
**Status:** Superseded — **não aplicar**  
**Substituída por:** `phase1-fixed-admin-login` (login fixo `admin` + `ADMIN_PASSWORD` no `.env`)  
**Relacionado:** `add-user-auth`, `limit-chargen-to-pregen-phase1`, `phase1-controlled-release-readiness`

---

## Why

Com `add-user-auth` aplicado, o desenvolvedor local precisa **cadastrar**, **copiar código do log** e **verificar e-mail** antes de jogar. Isso atrasa o ciclo de dev e expõe falhas de SMTP.

O objetivo é **segregar dev e produção** sem “burlar” o fluxo de login: em **development**, um **usuário master pré-provisionado** (`dev` / `dev`) entra pelo **`POST /auth/login` normal**, já verificado e com personagem starter. Em **production**, o fluxo completo de cadastro + verificação permanece.

---

## What Changes

### Variável de ambiente

| Variável | Valores | Default local |
|----------|---------|---------------|
| `APP_ENV` (backend) | `development` \| `production` | `development` se `DATABASE_PROFILE=sqlite-dev` |
| `NEXT_PUBLIC_APP_ENV` (frontend) | `development` \| `production` | espelha backend em `.env.local` |

### Usuário master (somente development)

| Campo | Valor |
|-------|--------|
| E-mail (canônico) | `dev@localhost` |
| Alias aceito no login (dev) | `dev` → normalizado para `dev@localhost` |
| Senha | `dev` |
| Verificado | Sim (`email_verified_at` setado) |
| Personagem | Starter WFRP4e criado se ausente |

Provisionado no **startup** do backend quando `APP_ENV=development` (idempotente: não duplica user/personagem).

### Comportamento por ambiente

| Fluxo | Development | Production |
|-------|-------------|------------|
| Usuário master | Criado/atualizado no startup | **Não existe** |
| `POST /auth/login` com `dev` / `dev` | ✓ JWT via login normal | ✗ 401 (conta inexistente) |
| `POST /auth/register` | Fluxo completo (para testar cadastro) | Fluxo completo + verify |
| `POST /auth/verify-email` | Fluxo completo (para testar UI) | Obrigatório no 1º cadastro |
| Envio de e-mail | `EMAIL_PROVIDER=mock` — log only | `EMAIL_PROVIDER=smtp` |

**Removido em relação ao draft anterior:** `POST /auth/dev/login`, register auto-verify, código fixo `00000000`, botão “Entrar como dev”.

### Frontend (development)

- Tela `/login`: hint discreto **“Desenvolvimento: dev / dev”**
- Opcional: pré-preencher e-mail `dev` e senha `dev` quando `NEXT_PUBLIC_APP_ENV=development`
- Fluxo idêntico ao login de produção (mesmo formulário, mesma API)

### Segurança

- Master user **nunca** provisionado com `APP_ENV=production`
- Startup **error** se `APP_ENV=production` + `JWT_SECRET` default ou `EMAIL_PROVIDER=mock`
- Documentar credenciais master **apenas** em README de dev local

---

## Capabilities

### Modified Capabilities

- `user-auth`: provisionamento master em dev; login alias `dev`; produção inalterada

---

## Impact

| Área | Alterações |
|------|------------|
| Backend | `config.py`, startup seed, `auth.py` alias login, testes |
| Frontend | hint + prefill opcional em `/login` |
| Docs | README, `.env.example` |

---

## Non-Goals

- Endpoint separado de dev login
- Auto-verify em register em dev
- OAuth, múltiplos usuários master
- Senha master configurável via env (fixo `dev` na fase 1)

---

## Open Questions (defaults assumidos)

| Questão | Decisão |
|---------|---------|
| E-mail canônico | `dev@localhost` |
| Login com alias | `dev` → `dev@localhost` só em `APP_ENV=development` |
| Senha master | `dev` (plaintext conhecido; só em dev local) |
| Rotacionar senha master | Não — recria DB local se necessário |
