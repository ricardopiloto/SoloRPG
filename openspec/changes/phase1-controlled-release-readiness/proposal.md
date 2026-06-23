# Proposal: phase1-controlled-release-readiness

**Data:** 2026-06-22  
**Status:** Draft  
**Relacionado:** `add-user-auth` (45/48), `limit-chargen-to-pregen-phase1` (código aplicado, tasks desatualizadas), `add-auth-dev-bypass` (0/20), `add-wfrp-solo-mvp` (loop de jogo base)

---

## Why

O projeto tem o **loop de jogo MVP** funcional e a **autenticação** quase completa, mas ainda não está pronto para um **teste controlado com usuários externos**. Faltam fechamento de escopo da fase 1 (pregens + starter, sem wizard), ergonomia de dev (bypass de verificação), endurecimento de produção, testes E2E com auth e validação manual documentada.

Esta change consolida o **gap analysis** e o **checklist de ship** — sem duplicar as features já especificadas em `add-auth-dev-bypass` e `limit-chargen-to-pregen-phase1`.

---

## Definição — MVP Fase 1 (teste controlado)

**Objetivo:** convidar um grupo pequeno a jogar campanhas WFRP solo com contas isoladas, onboarding rápido e superfície de ataque reduzida.

### Deve funcionar

| # | Capacidade | Critério de aceite |
|---|------------|-------------------|
| 1 | **Conta** | Fase 1: login fixo `admin` + `ADMIN_PASSWORD`; fase 2: register → verify → login; JWT |
| 2 | **Onboarding** | Após verify: personagem starter WFRP válido automático |
| 3 | **Personagens (fase 1)** | Starter + pré-gerados apenas — wizard oculto e API bloqueada |
| 4 | **Loop de jogo** | Home → campanha → sessão → rolagem → recap → progressão (atrás de login) |
| 5 | **Produção** | `JWT_SECRET` forte, `ADMIN_PASSWORD` forte, `APP_ENV=production`, CORS do frontend deployado |
| 6 | **Desenvolvimento** | Login admin com `ADMIN_PASSWORD` (sem cadastro/SMTP na fase 1) |
| 7 | **Qualidade** | pytest auth verde; E2E atualizado; checklist manual de onboarding + campanha |

### Fora da fase 1

- Wizard de criação custom (código permanece, flag off)
- OAuth, recuperação de senha, admin
- Paridade visual completa com protótipo OD
- CI/CD obrigatório (desejável, não blocker)
- Correção de todos os polish items pendentes (dice overlay, fate-fortune, etc.)

---

## Inventário — estado atual (2026-06-22)

### ✅ Concluído

| Área | Evidência |
|------|-----------|
| Auth backend | `auth_routes.py`, `User`, JWT, ownership, starter em verify |
| Auth frontend | `/login`, `/register`, `/verify-email`, `AuthProvider`, `RequireAuth` |
| Testes auth | 14/14 em `test_auth_*.py` |
| Chargen flag backend | `enable_custom_chargen=False`, `require_custom_chargen_enabled` em `deps.py` + `routes.py` |
| Chargen flag frontend | `customChargenEnabled` em `env.ts`; wizard oculto em `character/page.tsx` |
| Testes chargen guard | `test_custom_chargen_guard.py` |
| i18n pregen-only | `chargen.pageLeadPregenOnly` em `pt-BR.json` |
| Env template | `ENABLE_CUSTOM_CHARGEN`, `NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN` em `.env.example` |
| Loop de jogo | Campanhas, sessão, rolls, recap, progressão (pré-auth MVP) |

### ⚠️ Parcialmente feito

| Gap | Estado |
|-----|--------|
| `limit-chargen-to-pregen-phase1` | Código aplicado; `tasks.md` ainda 0/15; README linha 67 ainda menciona wizard |
| `add-user-auth` | 45/48; validação manual §9 pendente |
| pytest suite | 99 passed, **2 failed** (`test_images.py` — pipeline de imagens) |
| Documentação | `mvp-validation-checklist.md` sem passos de auth |

### ❌ Não feito (blockers para teste controlado)

| Gap | Change / ação |
|-----|----------------|
| Dev bypass de verificação | **`add-auth-dev-bypass`** — login master `dev`/`dev` via `/auth/login` |
| E2E com auth | `game-loop.spec.ts` vai direto a `/character` → redireciona para `/login` |
| Produção fail-fast | Sem validação de `JWT_SECRET` default em prod; sem `APP_ENV` |
| Deploy runbook | README §Deploy tem 3 linhas; sem checklist auth/SMTP/CORS |
| Rate limit register/login | Só resend tem cooldown 60s |
| Validação manual sign-off | `add-user-auth` 9.1–9.3; checklist campanha sem auth |

### 🔵 Opcional antes do teste (recomendado)

| Item | Risco se ignorar |
|------|------------------|
| Auth em `GET /images/{id}` | UUID guessing em deploy público |
| CI GitHub Actions | Regressões só detectadas manualmente |
| Toast boas-vindas starter (7.3) | UX menor; starter já aparece na lista |
| Corrigir `test_images.py` | `./scripts/run-tests.sh` falha como gate |

---

## What Changes (esta proposal)

Não implementa features novas além de **readiness gates**. Orquestra:

1. **Fechar** `limit-chargen-to-pregen-phase1` (sync tasks + docs)
2. **Aplicar** `add-auth-dev-bypass`
3. **Atualizar** E2E, checklist manual, deploy runbook
4. **Adicionar** guards de startup para produção
5. **Executar** validação manual e marcar sign-off

---

## Capabilities

### New Capabilities

- `release-readiness`: critérios de deploy, env matrix dev/prod, gates de teste e QA manual

### Modified Capabilities

- `dev-infrastructure`: E2E deve incluir fluxo de auth
- `user-auth`: referência cruzada a dev bypass (via `add-auth-dev-bypass`)

---

## Sequência recomendada

```
1. add-auth-dev-bypass          (~1 dia)   — dev friction
2. limit-chargen sync + docs    (~2 h)     — marcar tasks, README
3. phase1 readiness gates       (~1 dia)   — E2E, prod guards, checklist
4. Validação manual prod        (~2 h)     — register real ou staging SMTP
5. Deploy staging + convite     (~0.5 dia) — testers controlados
```

**Caminho crítico mínimo para liberar teste:** itens 2 + 3 + 4 (se testers usarem contas reais com SMTP). Item 1 é blocker apenas para **desenvolvimento local** ágil, não para testers em produção.

---

## Impact

| Área | Alterações |
|------|------------|
| OpenSpec | Sync tasks; archive quando sign-off |
| Backend | `APP_ENV`, startup guards (via add-auth-dev-bypass) |
| Frontend | Dev login button; E2E helper |
| Docs | `mvp-validation-checklist.md`, README deploy, `Docs/phase1-release-runbook.md` |
| Testes | E2E auth flow; opcional quarantine images |

---

## Non-Goals

- Implementar wizard ou novas mecânicas de jogo
- Multi-tenant billing ou convites por token
- Pen test formal ou SOC2

---

## Métrica de sucesso

- [ ] Tester externo completa: cadastro → verify → home com starter → pregen opcional → campanha → 1 sessão sem 401/403 inesperado
- [ ] Dev local entra com um clique (dev bypass)
- [ ] `./scripts/run-tests.sh` verde (ou gate documentado excluindo images)
- [ ] Deploy staging com `APP_ENV=production` + SMTP + JWT forte
