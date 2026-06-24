# Proposal: phase1-fixed-admin-login

**Data:** 2026-06-22  
**Status:** Draft  
**Supersede:** `add-auth-dev-bypass` (cancelar — não aplicar)  
**Relacionado:** `add-user-auth` (JWT + ownership permanecem; cadastro adiado), `limit-chargen-to-pregen-phase1`, `phase1-controlled-release-readiness` (atualizar escopo)

---

## Why

Para o **teste controlado da fase 1**, cadastro com verificação por e-mail adiciona fricção operacional (SMTP, múltiplas contas, suporte) sem valor imediato. O objetivo é validar o **loop de jogo** com acesso protegido, não multi-tenant completo.

A fase 1 terá **um único usuário fixo** (`admin`) com senha definida no `.env`. Sem tela de registro, sem verify-email, sem SMTP obrigatório.

O código de multi-usuário (`add-user-auth`) **permanece no repositório** mas fica **desligado** até a fase 2.

---

## What Changes

### Modo de autenticação fase 1

| Item | Comportamento |
|------|----------------|
| Usuário | Fixo: `admin` (e-mail canônico `admin@wfrp-solo.local`) |
| Senha | `ADMIN_PASSWORD` no `.env` do backend (**obrigatório**) |
| Provisionamento | Startup cria/atualiza hash do admin + starter se ausente |
| Login | `POST /auth/login` com `admin` + senha do env |
| Cadastro | **Removido da UI**; endpoints register/verify/resend retornam **404** |
| JWT | Mantido (sessão Bearer, 7 dias) |
| Multi-usuário | **Fora da fase 1** — todos os testers compartilham a mesma conta |

### Flag de controle

```env
AUTH_MODE=fixed_admin   # fase 1 (default)
# AUTH_MODE=multi_user  # fase 2 — reativa register/verify
```

### Backend

- `config.py`: `auth_mode`, `admin_password` (`ADMIN_PASSWORD`)
- `services/admin_user.py` — substitui `dev_master.py`; `ensure_admin_user()` em todo ambiente quando `fixed_admin`
- `authenticate_user`: em `fixed_admin`, só aceita admin + `ADMIN_PASSWORD`
- `validate_production_config`: exige `ADMIN_PASSWORD` (≥8 chars) + `JWT_SECRET` forte; **não** exige SMTP em `fixed_admin`
- Rotas register/verify/resend: `404` quando `AUTH_MODE=fixed_admin`

### Frontend

- `/login` — apenas senha (usuário fixo `admin`, campo oculto ou readonly)
- Remover links para `/register`; rotas `/register` e `/verify-email` redirecionam para `/login`
- Remover hint `dev/dev` e prefill de desenvolvimento
- i18n: copy “Digite a senha de acesso”

### Docs

- README, `.env.example`, `debian-server-install.md` — sem SMTP na fase 1
- `phase1-controlled-release-readiness` — escopo atualizado (conta única)

---

## Capabilities

### Modified Capabilities

- `user-auth`: modo `fixed_admin` com usuário admin e senha via env
- `web-interface`: login simplificado; sem cadastro
- `character-management`: starter no provisionamento do admin (não no verify)
- `release-readiness`: sem SMTP/multi-conta na fase 1

---

## Impact

| Área | Alterações |
|------|------------|
| Backend | config, admin_user seed, auth routes guard, production validation |
| Frontend | login only, remove register flow |
| Testes | auth tests adaptados a `fixed_admin`; pytest fixture usa `ADMIN_PASSWORD` |
| Docs | README, debian guide, mvp checklist |

---

## Non-Goals

- Múltiplos usuários ou isolamento por tester na fase 1
- OAuth, recuperação de senha
- Remover models `User`, JWT ou ownership (preparado para fase 2)
- Deletar código de register/verify (apenas desabilitado via flag)

---

## Trade-off explícito

**Conta compartilhada:** todos os testers na fase 1 veem os mesmos personagens e campanhas. Aceitável para grupo ≤10 em teste fechado. Fase 2 (`AUTH_MODE=multi_user`) restaura isolamento.

---

## Open Questions (defaults assumidos)

| Questão | Decisão |
|---------|---------|
| Nome de usuário | Fixo `admin` (não configurável) |
| Variável de senha | `ADMIN_PASSWORD` |
| E-mail canônico | `admin@wfrp-solo.local` |
| Default `AUTH_MODE` | `fixed_admin` |
| Register em testes fase 2 | `AUTH_MODE=multi_user` nos testes de cadastro |
