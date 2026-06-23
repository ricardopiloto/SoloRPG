# Proposal: add-user-auth

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `add-wfrp-solo-mvp` (sem auth hoje), `add-wfrp-character-creation-flow` (motor de criação para personagem aleatório), `Docs/database-schema.md` (tabela `players` planejada)

---

## Why

Hoje a aplicação não possui autenticação: qualquer cliente lista e cria personagens, campanhas e sessões sem identidade. Isso impede multi-usuário seguro, isolamento de dados e evolução para deploy público.

O jogador precisa de uma **conta própria** (e-mail + senha) com **verificação de e-mail no primeiro cadastro** e acesso restrito aos **personagens da sua conta**. Todo novo cadastro verificado recebe automaticamente um **personagem aleatório válido** para entrar no jogo sem passar pelo wizard manual.

---

## What Changes

### Cadastro e verificação

| Etapa | Comportamento |
|-------|----------------|
| **Cadastro** | E-mail válido + senha + confirmação de senha |
| **Validação** | Formato de e-mail (RFC), senhas iguais, senha mínima 8 caracteres |
| **Verificação** | Código numérico único de **8 dígitos** enviado ao e-mail; solicitado **apenas no primeiro cadastro** |
| **Pós-verificação** | Conta marcada como verificada; personagem aleatório criado; usuário pode fazer login |

Login com e-mail + senha **bloqueado** até a verificação concluir. Reenvio de código permitido com rate limit.

### Autenticação e autorização

- Sessão via **JWT** (Bearer token) emitido no login e após verificação bem-sucedida
- Endpoints de personagem, campanha e sessão exigem usuário autenticado
- `GET /characters` e demais leituras retornam **somente** personagens com `user_id` do token
- Tentativa de acessar recurso de outro usuário → `403 Forbidden`

### Personagem aleatório no cadastro

Após verificação do e-mail, o backend gera automaticamente um personagem WFRP4e válido usando o motor existente (`character_creation.py`):

- Espécie Humano (MVP)
- Carreira rolada na tabela d100
- Atributos rolados `2d10+20`
- Alocação mínima válida de perícias/talentos/Destino
- Nome gerado a partir de pool PT-BR ou sufixo aleatório (ex.: *"Soldado de Reikland #4821"*)

O jogador pode criar personagens adicionais pelo wizard existente; todos ficam vinculados à conta.

### Backend

- Model `User` (`users`): `email`, `password_hash`, `email_verified_at`, timestamps
- Model `EmailVerificationCode`: código 8 dígitos, expiração, tentativas
- `user_id` FK em `player_characters` (NOT NULL para novos registros)
- Adapter de e-mail (`get_email_adapter()`): `mock` (log/dev) e `smtp` (prod)
- Endpoints:
  - `POST /auth/register`
  - `POST /auth/verify-email`
  - `POST /auth/resend-verification`
  - `POST /auth/login`
  - `GET /auth/me`
- Dependency `get_current_user` em rotas protegidas

### Frontend

- Páginas `/login`, `/register`, `/verify-email`
- Contexto de auth + token em `localStorage` (ou cookie httpOnly se implementado no backend)
- Rotas protegidas redirecionam para login
- Home e `/character` operam no escopo do usuário logado
- i18n PT-BR: `auth.*`

---

## Capabilities

### New Capabilities

- `user-auth`: cadastro, verificação por código, login, sessão JWT, envio de e-mail

### Modified Capabilities

- `character-management`: ownership por usuário; personagem aleatório no cadastro; criação/listagem escopada
- `web-interface`: telas de auth, guard de rotas, fluxo pós-cadastro

---

## Impact

| Área | Alterações |
|------|------------|
| Backend | models, migration, auth service, email adapter, JWT, routes, ownership checks |
| Frontend | login/register/verify pages, auth context, api headers, route guards |
| Testes | auth unit/integration, ownership 403, mock email, starter character |
| Dev | `.env.example` com `JWT_SECRET`, `EMAIL_PROVIDER`, SMTP vars |
| Docs | `Docs/database-schema.md` alinhado; README fluxo de conta |

---

## Non-Goals

- OAuth / login social (Google, etc.)
- Recuperação de senha (“esqueci minha senha”) — follow-up
- Multi-dispositivo / refresh token — follow-up
- Admin panel ou roles
- Verificação de e-mail em re-cadastro ou troca de e-mail

---

## Open Questions (defaults assumidos na proposta)

| Questão | Decisão proposta |
|---------|------------------|
| Personagens existentes sem `user_id` | Ocultos; dev recria DB ou script de migração manual |
| Onde guardar JWT no frontend | `localStorage` + header `Authorization` (MVP) |
| Expiração do código | 15 minutos; máx. 5 tentativas erradas |
| Expiração do JWT | 7 dias |
