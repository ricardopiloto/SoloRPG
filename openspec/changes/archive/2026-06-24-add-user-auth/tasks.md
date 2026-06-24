# Tasks: add-user-auth

## 1. Modelo e migration

- [x] 1.1 Model `User` em `backend/app/db/models.py` (`email`, `password_hash`, `email_verified_at`)
- [x] 1.2 Model `EmailVerificationCode` (hash do código, expiração, tentativas, `used_at`)
- [x] 1.3 Colunas `user_id` (FK) e `is_starter` em `PlayerCharacter`
- [x] 1.4 Migration Alembic `0003_add_user_auth` (+ patch sqlite dev se necessário)
- [x] 1.5 Índice único em `users.email` (lowercase)

## 2. Auth core (backend)

- [x] 2.1 `backend/app/services/auth.py` — hash/verify senha (bcrypt), normalização de e-mail
- [x] 2.2 `backend/app/services/jwt_tokens.py` — criar/decodificar JWT (`JWT_SECRET`, exp 7d)
- [x] 2.3 `backend/app/api/deps.py` — `get_current_user`, `get_verified_user`
- [x] 2.4 Schemas: `RegisterRequest`, `LoginRequest`, `VerifyEmailRequest`, `AuthTokenOut`, `UserOut`
- [x] 2.5 `POST /auth/register` — valida senha+confirmação, cria user unverified, dispara e-mail
- [x] 2.6 `POST /auth/verify-email` — valida código 8 dígitos, marca verified, retorna JWT
- [x] 2.7 `POST /auth/resend-verification` — novo código, rate limit 1/min
- [x] 2.8 `POST /auth/login` — bloqueia unverified (403), emite JWT
- [x] 2.9 `GET /auth/me` — usuário atual

## 3. Email adapter

- [x] 3.1 `backend/app/email/adapter.py` — protocol + `get_email_adapter()`
- [x] 3.2 Provider `mock` — log do código (testes/dev)
- [x] 3.3 Provider `smtp` — env vars + template PT-BR
- [x] 3.4 Config em `backend/app/config.py`: `EMAIL_PROVIDER`, SMTP vars, `JWT_SECRET`
- [x] 3.5 Atualizar `.env.example` (raiz)

## 4. Personagem aleatório + ownership

- [x] 4.1 `backend/app/services/starter_character.py` — `generate_random_starter_character(user_id)` via `character_creation.py`
- [x] 4.2 Chamar starter character em `verify-email` (transação: verify + create char + JWT)
- [x] 4.3 `create_character` / `create_from_pregen` / wizard — exigir `user_id` do token
- [x] 4.4 `list_characters`, `get_character`, progression — filtrar/validar ownership (`403` se outro user)
- [x] 4.5 Campanhas e sessões — validar que `character.user_id == current_user.id` na cadeia
- [x] 4.6 Testes: starter válido WFRP, list só retorna chars do user, 403 cross-user

## 5. Testes backend

- [x] 5.1 `test_auth_register.py` — happy path, email inválido, senha curta, mismatch confirmação
- [x] 5.2 `test_auth_verify.py` — código correto, expirado, tentativas excedidas, reenvio
- [x] 5.3 `test_auth_login.py` — login ok, credenciais erradas, unverified blocked
- [x] 5.4 `test_auth_ownership.py` — endpoints protegidos sem token 401, cross-user 403
- [x] 5.5 Atualizar `test_api_integration.py` — helper `register_and_login()` com mock email

## 6. Frontend auth

- [x] 6.1 Tipos + `api.register`, `api.verifyEmail`, `api.login`, `api.me`, header Bearer
- [x] 6.2 `AuthProvider` + hook `useAuth` (token em localStorage)
- [x] 6.3 Página `/register` — e-mail, senha, confirmar senha, validação client-side
- [x] 6.4 Página `/verify-email` — input código 8 dígitos, reenviar, redirect pós-sucesso
- [x] 6.5 Página `/login` — e-mail/senha, redirect se unverified
- [x] 6.6 Route guard — páginas principais redirecionam para `/login` se não autenticado
- [x] 6.7 AppShell/nav — logout, exibir e-mail ou avatar placeholder
- [x] 6.8 i18n `auth.*` em `messages/pt-BR.json`

## 7. Integração UX

- [x] 7.1 Home pós-login — lista personagens do usuário (inclui starter)
- [x] 7.2 `/character` — wizard e pregens exigem login; personagens criados com ownership
- [x] 7.3 Mensagem de boas-vindas quando conta nova tem apenas starter (opcional toast)
- [x] 7.4 `npm run build` + `pytest` verdes

## 8. Documentação

- [x] 8.1 Atualizar README — fluxo de conta, vars JWT/EMAIL
- [x] 8.2 Alinhar `Docs/database-schema.md` — tabela `users`, FK em characters
- [x] 8.3 Nota dev: recriar sqlite ou migrar após pull

## 9. Validação manual

- [ ] 9.1 Cadastro → receber código (mock log) → verify → home com personagem aleatório
- [ ] 9.2 Login após verify; tentativa login antes de verify redireciona
- [ ] 9.3 Segunda conta não vê personagens da primeira
