# Design: add-auth-dev-bypass

## Context

**Estado atual**

- Auth completo com register → verify → login.
- `EMAIL_PROVIDER=mock` loga código, mas dev ainda precisa cadastrar.
- Draft anterior previa `POST /auth/dev/login` e bypasses — **substituído** por usuário master + login normal.

**Motivação do refinamento**

O desenvolvedor prefere **não burlar** o fluxo de autenticação: usa o mesmo `/login` que produção, com credenciais fixas conhecidas (`dev` / `dev`).

---

## Goals / Non-Goals

**Goals**

- `APP_ENV` explícito dev vs prod.
- Usuário master provisionado automaticamente em dev.
- Login `dev` / `dev` via `POST /auth/login`.
- Produção sem master user e com verify obrigatório.

**Non-Goals**

- Endpoint `/auth/dev/login`.
- Register/verify bypass em dev.
- Master user em produção.

---

## Decisions

### 1. `APP_ENV`

```python
app_env: str = "development"  # development | production

@property
def is_production(self) -> bool:
    return self.app_env.lower() == "production"
```

Default: `development` se `DATABASE_PROFILE=sqlite-dev`, senão `production`.

### 2. Master user seed (startup)

```python
DEV_MASTER_EMAIL = "dev@localhost"
DEV_MASTER_PASSWORD = "dev"
DEV_MASTER_ALIAS = "dev"

async def ensure_dev_master_user(db):
    if settings.is_production:
        return
    user = await get_user_by_email(db, DEV_MASTER_EMAIL)
    if not user:
        user = await create_user(db, DEV_MASTER_EMAIL, DEV_MASTER_PASSWORD)
        user.email_verified_at = now()
        await db.commit()
    elif user.email_verified_at is None:
        user.email_verified_at = now()
        await db.commit()
    if not await user_has_characters(db, user.id):
        await generate_random_starter_character(db, user.id)
```

Chamado em `lifespan` após `create_all` / patches.

**Alternativa rejeitada:** senha aleatória + log — dev teria que copiar do console (mesma fricção).

### 3. Login alias em dev

```python
def normalize_login_email(email: str) -> str:
    e = email.strip().lower()
    if not settings.is_production and e == "dev":
        return DEV_MASTER_EMAIL
    return e
```

Usado em `authenticate_user` e `login` handler.

### 4. Sem bypass em register/verify

Register e verify permanecem **idênticos** em dev e prod para quem quiser testar onboarding. Caminho feliz do dev diário: **só login master**.

### 5. Frontend

```tsx
// login page — quando isDevAppEnv
<p className="text-xs text-wfrp-muted">{t("auth.devMasterHint")}</p>
// optional defaultValues: email "dev", password "dev"
```

Sem botão extra; sem `api.devLogin()`.

### 6. Produção guards (startup)

```python
if settings.is_production:
    if settings.jwt_secret.startswith("change-me"):
        raise RuntimeError("JWT_SECRET must be set in production")
    if settings.email_provider != "smtp":
        logger.warning("EMAIL_PROVIDER should be smtp in production")
```

### 7. Testes

- `test_auth_dev_master.py`: após startup em dev, login dev/dev → 200 + JWT
- Login `dev@localhost` / `dev` → 200
- Com `APP_ENV=production`, login dev/dev → 401
- Master user não criado em prod fixture

---

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Credencial fraca vazada | Só existe em dev; nunca seed em prod |
| Deploy com APP_ENV errado | Default production for non-sqlite; startup guards |
| E-mail `dev@localhost` inválido no form | Alias `dev` no backend; hint na UI |

---

## Migration Plan

1. Config `APP_ENV`
2. `ensure_dev_master_user` no lifespan
3. Alias login em `auth.py`
4. Frontend hint + prefill
5. Testes + README
6. Atualizar referências em `phase1-controlled-release-readiness` (dev login → master user)

Sem migration de banco.
