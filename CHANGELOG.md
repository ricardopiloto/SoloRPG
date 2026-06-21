# Changelog

Todas as mudanças relevantes do **WFRP Solo** são documentadas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).  
Versionamento segue o repositório Git — rastreie também as propostas em `openspec/changes/`.

---

## [Unreleased]

Alterações locais ainda **não commitadas** (desde o clone/sync de 2026-06-20).

### Added

- **skill-row-wfrp-advance-format** — formato WFRP `4+[Fel]` na sidebar de perícias (antes `[Fel] +4`)
  - `formatSkillRowMeta()` atualizado em `frontend/src/lib/wfrp-attributes.ts`
  - Testes unitários em `frontend/src/lib/wfrp-attributes.test.ts`
  - Script `npm run test:unit` no frontend
  - Proposta OpenSpec: `openspec/changes/skill-row-wfrp-advance-format/` ✅ 11/11 tasks

- **session-image-credits-guard** — guarda de créditos Cloudflare para geração de imagens
  - Coluna `images_enabled` em `GameSession` + migration `0002_add_images_enabled`
  - `probe_image_credits()` e `is_quota_or_credit_error()` em `cloudflare_workers_ai.py`
  - Probe síncrono em `start_session()`; guard em `[IMAGEM]` quando desabilitado
  - Desligamento mid-session em falha de quota; campo na API (`SessionOut`)
  - 9 testes em `backend/tests/test_session_image_credits_guard.py`
  - Proposta OpenSpec: `openspec/changes/session-image-credits-guard/` — 18/21 tasks (validação manual CF pendente)

- **add-fate-fortune-mechanics** — proposta OpenSpec (não implementada)
  - Destino: evitar ferimento ou morte, nunca recupera
  - Fortuna: re-roll de teste falho, refresh por sessão = `fate_current`
  - Proposta: `openspec/changes/add-fate-fortune-mechanics/` — 0/27 tasks

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

## Status das changes OpenSpec (2026-06-21)

| Change | Tasks | Status |
|--------|-------|--------|
| `skill-row-wfrp-advance-format` | 11/11 | ✅ Completo (local, uncommitted) |
| `session-image-credits-guard` | 18/21 | 🟡 Implementado — validação manual CF pendente |
| `add-fate-fortune-mechanics` | 0/27 | 📋 Proposta — aguardando `/opsx:apply` |
| `add-wfrp-solo-mvp` | 64/66 | 🟡 Quase completo |
| `add-3d-dice` | 25/29 | 🟡 Em progresso |
| `upgrade-3d-dice-dsn-fidelity` | 24/26 | 🟡 Em progresso |
| `add-diary-npc-roster` | 14/16 | 🟡 Em progresso |
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

[Unreleased]: https://github.com/ricardopiloto/SoloRPG/compare/main...HEAD
[0.1.0]: https://github.com/ricardopiloto/SoloRPG/commit/de931ad
