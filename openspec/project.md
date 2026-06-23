# Project Context

## Purpose

WFRP Solo is a web application for solo tabletop RPG play where an LLM acts as a synthetic Game Master with its own narrative agenda, persistent memory across sessions, and full WFRP4e (Warhammer Fantasy Roleplay 4th Edition) campaign support. The player interacts exclusively via free text. The central principle: for the player, it should be irrelevant whether the GM is human or AI.

## Tech Stack

- **Frontend:** Next.js 14 (App Router), TailwindCSS, shadcn/ui, next-intl
- **Backend:** Python + FastAPI
- **Database:** SQLite (`aiosqlite`) — single file `wfrp_solo.db`
- **Semantic memory:** JSON embeddings + Python cosine search (`PythonSearchAdapter`)
- **LLM:** DeepSeek (`deepseek-chat`) default; adapter suporta mock / Claude
- **Image generation:** Cloudflare Workers AI (`flux-1-schnell`, async background queue)
- **Deploy:** Vercel (frontend), Railway/Fly.io or VPS Debian (backend + SQLite file)

## Project Conventions

### Code Style
- TypeScript on frontend; Python on backend
- PT-BR for all user-facing strings; externalized via i18n from day one
- Server-side game mechanics; never delegate dice or wounds to LLM

### Architecture Patterns
- **Separation of concerns:** Rules engine (deterministic code) / Narrative (LLM) / Memory (database)
- **Signal protocol:** LLM emits tagged JSON signals (`[TESTE]`, `[IMAGEM]`, etc.); backend parses and executes
- **Four-layer memory:** Relational facts → Python semantic search → compressed LLM summaries → active session turn history
- **Two session modes:** EXPLORACAO (time-based) and COMBATE (turn-based)

### Testing Strategy
- Unit tests for WFRP rules engine (dice, combat, wounds, XP, progression)
- Integration tests for signal parsing and LLM loop (mocked LLM)
- API tests for character, campaign, and session lifecycle
- E2E test for main loop: auth → pregen → session → XP → progression

### Git Workflow
- Feature branches; conventional commit messages
- OpenSpec-driven: proposals in `openspec/changes/`, specs in `openspec/specs/` after archive

## Domain Context

- Based on WFRP4e mechanics: d100 tests, careers, wounds, Fate/Fortune Points, skills, talents
- Insanity/Corruption mechanics excluded from MVP
- Permanent death when Fate Points exhausted
- Campaigns can end by completion, death (unfinished), or player choice
- Identity layers (karma, reputation, social perception) are narrative-only — never shown as numbers
- GM system prompt defined in `Docs/gm-system-prompt.md`

## Important Constraints

- MVP is a personal project with qualitative success metrics
- Sessions are pausable; player can pause and resume at any time. Duration is announced before start.
- Native PT-BR; i18n-ready architecture
- No multiplayer, no videogame controls, no monetization, no native mobile app
- Fate Points do not reset between campaigns in MVP
- SQLite: single uvicorn worker recommended in production

## External Dependencies

- LLM API (Anthropic Claude / DeepSeek) — model-agnostic adapter required
- Cloudflare Workers AI API — async image generation (FLUX.1 Schnell)
- SMTP — email verification in production
- Vercel — frontend hosting (optional)

## Reference Documents

- `Docs/README.md` — documentation index
- `Docs/architecture.md` — architecture, flows, frontend/backend split
- `Docs/product-brief.md` — product requirements and MVP scope
- `Docs/ux-spec.md` — UI/UX design spec (grimório palette, 9 screens)
- `Docs/database-schema.md` — SQLite schema + JSON embeddings
- `Docs/debian-server-install.md` — Debian/Ubuntu server deployment guide
- `Docs/gm-system-prompt.md` — GM persona and signal protocol
- `Docs/mvp-validation-checklist.md` — manual QA checklist
