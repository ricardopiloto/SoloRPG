# Changelog

Todas as mudanças relevantes do **WFRP Solo** são documentadas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).  
Versionamento segue o repositório Git — rastreie também as propostas em `openspec/changes/`.

---

## [Unreleased]

Alterações locais ainda **não commitadas**.

### Added

- **add-wfrp-character-creation-flow** — assistente de criação WFRP4e em etapas (substitui formulário custom livre)
  - **Backend:** `character_creation.py`, catálogo de espécies (`species.py`), carreiras Tier 1 Core (`careers_catalog.json`), perícias básicas (`skills_basic.py`)
  - Endpoints: `GET /rules/character-creation`, `GET /rules/careers`, `POST /characters/validate-creation`, `POST /characters` (somente rascunho validado)
  - Rolagem `2d10+20` ou point-buy (4–18), swap/reroll, XP de criação, derivados (ferimentos, Destino/Fortuna, perícias básicas)
  - **Background com IA:** `POST /characters/generate-background` + prompt dedicado `Docs/character-background-prompt.md` (mesma LLM, sem prompt de GM)
  - **Frontend:** `CharacterCreationWizard` na aba **Criar personagem** em `/character`; i18n `chargen.*`
  - Testes: `test_character_creation.py`, `test_character_background.py`, integração em `test_api_integration.py`
  - Proposta OpenSpec: `openspec/changes/add-wfrp-character-creation-flow/` — 36/38 tasks (validação manual 4.5/4.6 pendente)

### Fixed

- **GET /rules/careers** — `ResponseValidationError` ao abrir o assistente (`career_class` vs. alias `class` em `CareerSummaryOut`)
  - `CareerSummaryOut.career_class` com `Field(alias="class")` em `backend/app/schemas/api.py`
  - Teste `test_api_list_careers_returns_class_field` em `test_api_integration.py`

---

## [0.3.1] — 2026-06-23

Hotfix de produção — system prompt do GM não carregava no container Docker.

### Fixed

- **fix-docker-gm-prompt** — `Docs/gm-system-prompt.md` não era copiado para dentro do container do backend
  - O `docker-compose.yml` usava `context: ./backend`, que não enxergava a pasta `Docs/` na raiz do projeto
  - O `prompts.py` calculava o path como `parents[3] / "Docs"` → `/Docs/` dentro do container — inexistente → caía silenciosamente no `_fallback_prompt()` (3 linhas)
  - O GM respondia com o fallback mínimo: sinais `[TESTE]` e `[IMAGEM]` gerados como texto livre em vez de JSON estruturado, tornando-os invisíveis na UI (parser ignorava)
  - **Correção:** build context mudado para `.` (raiz do projeto); `COPY Docs /Docs` adicionado ao `backend/Dockerfile`; `.dockerignore` criado na raiz para excluir artefatos desnecessários do context
  - **Reforço de prompt:** seção "ERRADO vs CORRETO" adicionada ao `gm-system-prompt.md` com exemplos explícitos do formato JSON obrigatório para `[TESTE]` e `[IMAGEM]`

---

## [0.3.0] — 2026-06-22

Release de **prontidão fase 1** — conta única, SQLite-only, chargen restrito e superfície de auth reduzida para teste controlado.

### Added

- **phase1-fixed-admin-login** — login fixo fase 1
  - `AUTH_MODE=fixed_admin` (padrão) + `ADMIN_PASSWORD` obrigatório (≥8 chars) no `.env`
  - Usuário seed `admin` (`admin@wfrp-solo.local`) com personagem starter no startup
  - `GET /api/auth/config` → `{ auth_mode, login_username, registration_enabled }`
  - Register, verify e resend retornam **404** em `fixed_admin`
  - **Frontend:** `/login` só senha; `/register` e `/verify-email` redirecionam para login
  - Testes: `test_admin_login.py`; E2E com `admin` + `ADMIN_PASSWORD`
  - Proposta OpenSpec: `openspec/changes/phase1-fixed-admin-login/` ✅ 7/7 tracks

- **add-user-auth** — autenticação JWT e isolamento por conta
  - Register → verify e-mail → login (modo `multi_user`, fase 2)
  - Personagem starter automático após verify; dados isolados por usuário
  - Proposta OpenSpec: `openspec/changes/add-user-auth/`

- **limit-chargen-to-pregen-phase1** — criação custom desligada na fase 1
  - `ENABLE_CUSTOM_CHARGEN=false`; wizard oculto na UI; API bloqueada
  - Caminhos ativos: starter + pré-gerados em `/character`
  - Proposta OpenSpec: `openspec/changes/limit-chargen-to-pregen-phase1/`

### Changed

- **sqlite-only-database** — SQLite como único backend suportado
  - Removidos PostgreSQL, pgvector e `docker-compose.yml`
  - Memória semântica via `PythonSearchAdapter` (sem pgvector)
  - Proposta OpenSpec: `openspec/changes/sqlite-only-database/`

- **phase1-controlled-release-readiness** — documentação e gates de release
  - README, `.env.example`, `Docs/debian-server-install.md`, checklist MVP
  - SMTP obrigatório apenas em `AUTH_MODE=multi_user` + production

### Removed

- **add-auth-dev-bypass** — superseded por `phase1-fixed-admin-login`
  - Removidos usuário `dev@localhost` / `dev` e hint `dev/dev` na UI

---

## [0.2.0] — 2026-06-21

Commit `74c6086` — Destino/Fortuna, dados 3D, guarda de imagens, roster de NPCs no diário.

### Added

- **add-fate-fortune-mechanics** — regras completas de Destino e Fortuna
  - Destino: evitar ferimento ou morte; nunca recupera
  - Fortuna: re-roll de teste falho; refresh no início da sessão = `fate_current`
  - `fortune_*` derivado de `fate_current`; removido bônus legado `+10`
  - UI: gemas Destino e Fortuna na sidebar; fluxo de gasto em testes
  - 236 linhas de testes em `test_fate_fortune_mechanics.py`
  - Proposta OpenSpec: `openspec/changes/add-fate-fortune-mechanics/` — 23/27 tasks

- **fortune-one-reroll-per-test** — um re-roll de Fortuna por teste pendente (server-side)
  - Proposta OpenSpec: `openspec/changes/fortune-one-reroll-per-test/` — 10/12 tasks

- **fix-dice-overlay-zenbrowser** — init robusto do DiceBox 3D
  - Singleton `diceBoxHost.ts` com promise de init, dimensões mínimas do stage, fallback RNG
  - Proposta OpenSpec: `openspec/changes/fix-dice-overlay-zenbrowser/` — 7/9 tasks

- **session-image-credits-guard** — guarda de créditos Cloudflare para geração de imagens
  - Coluna `images_enabled` em `GameSession` + migration `0002_add_images_enabled`
  - `probe_image_credits()` e `is_quota_or_credit_error()` em `cloudflare_workers_ai.py`
  - Probe em `start_session()`; guard em `[IMAGEM]` quando desabilitado
  - 9 testes em `backend/tests/test_session_image_credits_guard.py`
  - Proposta OpenSpec: `openspec/changes/session-image-credits-guard/` — 18/21 tasks (validação manual CF pendente)

- **add-diary-npc-roster** — roster de NPCs conhecidos na aba Personagem do diário
  - Campos `known_name` e `met_location` no model `NPC`; `GET /campaigns/{id}/npcs`
  - `knownNpcs` em `useSessionPlay`; lista na `DiarySidebar`
  - Proposta OpenSpec: `openspec/changes/add-diary-npc-roster/` — 14/16 tasks (validação manual 5.2/5.3 pendente)

- **skill-row-wfrp-advance-format** — formato WFRP `4+[Fel]` na sidebar de perícias (antes `[Fel] +4`)
  - `formatSkillRowMeta()` em `frontend/src/lib/wfrp-attributes.ts` + testes unitários
  - Script `npm run test:unit` no frontend
  - Proposta OpenSpec: `openspec/changes/skill-row-wfrp-advance-format/` ✅ 11/11 tasks

- **Docs/export-propostas-recentes.md** — export consolidado de propostas recentes

### Changed

- OpenSpec: instruções movidas para `openspec/config.yaml` (removido `openspec/AGENTS.md` duplicado)

---

## [0.1.0] — 2026-06-20

Commit inicial (`de931ad`) — baseline do MVP WFRP Solo entregue no GitHub.

### Added — Core MVP (`add-wfrp-solo-mvp`)

- Aplicação web solo RPG WFRP4e com GM sintético (LLM)
- **Backend:** FastAPI, SQLAlchemy, SQLite dev / PostgreSQL prod
- **Frontend:** Next.js 14, TailwindCSS, TypeScript
- Motor de regras d100: atributos, perícias, combate, críticos, Fate/Fortune (parcial)
- Protocolo de sinais GM: `[TESTE]`, `[IMAGEM]`, `[FIM_SESSAO]`, `[ACAO_SISTEMA]`, etc.
- Gestão de personagem, campanha, sessão e memória narrativa
- Personagens pré-gerados (Helena Krauss, Tobias Grimm)
- Integração LLM DeepSeek (adapter mock/Claude/DeepSeek)

### Added — Infraestrutura e dev (`archive/2026-06-17-*`)

| Change | Entrega principal |
|--------|-------------------|
| `add-local-db-alternatives` | Perfis sqlite-dev, postgres (Docker), supabase |
| `configure-deepseek-llm` | Adapter DeepSeek como provider padrão |
| `add-mvp-quality-gates` | Testes, lint, checklist de validação MVP |
| `update-docs-stack-alignment` | README, `.env.example`, scripts de dev |

### Added — Campanha e sessão

| Change | Entrega principal |
|--------|-------------------|
| `add-campaign-flows` | Fluxo criar campanha → sessão → jogo |
| `add-session-pause-resume` | Pausar/retomar sessão, timer congelado |
| `add-combat-orchestration` | Modo combate, iniciativa, turnos |
| `improve-session-end-flow` | Tela fim de sessão, XP, resumo (parcial) |
| `update-session-pausable-ux` | UX de pausa na interface (parcial) |

### Added — Interface e UX

| Change | Entrega principal |
|--------|-------------------|
| `add-frontend-prototype-parity` | AppShell, sidebars, wounds bar, fate gems, colapsáveis |
| `add-quick-roll-sidebar` | Quick roll em atributos/perícias/armas |
| `update-character-sidebar-stats-ui` | Cards compactos 5×2, lista de perícias do catálogo |
| `refine-skill-row-target-display` | Meta `[Attr] +N` na linha de perícia |
| `fix-session-sidebar-layout` | Layout responsivo das sidebars |
| `add-game-chat-ux` | Chat de sessão, markdown narrativo, blocos de teste |
| `refactor-inline-chat-dice-roll` | Rolagem inline no chat |
| `refine-chat-attribution-visual` | Distinção visual GM vs. jogador (parcial) |
| `fix-chat-scroll-containment` | Scroll contido no painel de chat (parcial) |
| `add-diary-npc-roster` | Diário lateral + roster de NPCs (parcial) |

### Added — Dados e memória

| Change | Entrega principal |
|--------|-------------------|
| `complete-memory-identity` | Fortune spend, camadas NPC conhecidos, patches schema |
| `update-gm-prompt-perception` | Percepção social no contexto GM |
| `sync-gm-prompt-v23` | Sincronização prompt GM v2.3 (parcial) |

### Added — Combate e agency

| Change | Entrega principal |
|--------|-------------------|
| `add-player-test-agency` | Jogador rola dados em testes GM (não auto-roll) |

### Added — Assets visuais

| Change | Entrega principal |
|--------|-------------------|
| `add-flux-visual-pipeline` | Pipeline assíncrono de imagens (base) |
| `switch-to-cloudflare-workers-ai` | Migração Flux → Cloudflare Workers AI |
| `handle-image-api-failure` | Falha silenciosa de imagens (sem placeholder) |
| `fix-silent-api-failures` | Erros de API sem quebrar UX (parcial) |

### Added — Dados 3D

| Change | Entrega principal |
|--------|-------------------|
| `add-3d-dice` | Dice-box 3D no overlay de rolagem |
| `upgrade-3d-dice-dsn-fidelity` | Fidelidade visual dos dados (parcial) |
| `fix-dice-box-v11-api` | Compatibilidade API dice-box v1.1 (parcial) |

---

## Status das changes OpenSpec (2026-06-22)

| Change | Tasks | Status |
|--------|-------|--------|
| `phase1-fixed-admin-login` | 7/7 | ✅ Completo |
| `sqlite-only-database` | — | ✅ Completo |
| `limit-chargen-to-pregen-phase1` | — | ✅ Completo |
| `add-user-auth` | 45/48 | 🟡 Quase completo |
| `phase1-controlled-release-readiness` | — | 🟡 Em progresso |
| `add-wfrp-character-creation-flow` | 36/38 | 🟡 Implementado (local) — validação manual pendente |
| `skill-row-wfrp-advance-format` | 11/11 | ✅ Completo |
| `session-image-credits-guard` | 18/21 | 🟡 Implementado — validação manual CF pendente |
| `add-fate-fortune-mechanics` | 23/27 | 🟡 Implementado — validação manual pendente |
| `fortune-one-reroll-per-test` | 10/12 | 🟡 Implementado — validação manual pendente |
| `fix-dice-overlay-zenbrowser` | 7/9 | 🟡 Implementado — validação manual pendente |
| `add-diary-npc-roster` | 14/16 | 🟡 Implementado — validação manual pendente |
| `add-wfrp-solo-mvp` | 64/66 | 🟡 Quase completo |
| `add-3d-dice` | 25/29 | 🟡 Em progresso |
| `upgrade-3d-dice-dsn-fidelity` | 24/26 | 🟡 Em progresso |
| `add-game-chat-ux` | 16/18 | 🟡 Em progresso |
| `handle-image-api-failure` | 9/16 | 🟡 Em progresso |
| `improve-session-end-flow` | 14/19 | 🟡 Em progresso |
| `update-character-sidebar-stats-ui` | 17/20 | 🟡 Em progresso |
| `fix-chat-scroll-containment` | 10/16 | 🟡 Em progresso |
| `fix-dice-box-v11-api` | 9/11 | 🟡 Em progresso |
| `fix-silent-api-failures` | 5/7 | 🟡 Em progresso |
| `refine-skill-row-target-display` | 6/9 | 🟡 Supersedido por `skill-row-wfrp-advance-format` |
| `refine-chat-attribution-visual` | 7/11 | 🟡 Em progresso |
| `sync-gm-prompt-v23` | 9/15 | 🟡 Em progresso |
| `update-gm-prompt-perception` | 9/13 | 🟡 Em progresso |
| `update-session-pausable-ux` | 9/11 | 🟡 Em progresso |

Changes arquivadas em `openspec/changes/archive/2026-06-17-*/` estão incorporadas no baseline 0.1.0.

---

## Como manter este changelog

1. **A cada feature implementada:** adicione entrada em `[Unreleased]` com link à change OpenSpec.
2. **Ao commitar:** mova `[Unreleased]` para nova versão datada (`[0.2.0] — YYYY-MM-DD`).
3. **Ao arquivar change:** rode `/opsx:archive` e atualize a tabela de status.
4. **Referência:** propostas detalhadas em `openspec/changes/<nome>/proposal.md`.

---

[Unreleased]: https://github.com/ricardopiloto/SoloRPG/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/ricardopiloto/SoloRPG/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/ricardopiloto/SoloRPG/compare/74c6086...v0.3.0
[0.2.0]: https://github.com/ricardopiloto/SoloRPG/compare/de931ad...74c6086
[0.1.0]: https://github.com/ricardopiloto/SoloRPG/commit/de931ad
