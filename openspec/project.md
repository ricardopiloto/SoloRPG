# Project Context

## Purpose

WFRP Solo is a web application for solo tabletop RPG play where an LLM acts as a synthetic Game Master with its own narrative agenda, persistent memory across sessions, and full WFRP4e (Warhammer Fantasy Roleplay 4th Edition) campaign support. The player interacts exclusively via free text. The central principle: for the player, it should be irrelevant whether the GM is human or AI.

## Tech Stack

- **Frontend:** Next.js 14 (App Router), TailwindCSS, shadcn/ui, next-intl
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL + pgvector (Supabase for MVP)
- **LLM:** DeepSeek (`deepseek-chat`) default; adapter suporta mock / Claude
- **Image generation:** Cloudflare Workers AI (`flux-1-schnell`, async background queue)
- **Deploy:** Vercel (frontend), Railway/Fly.io (backend), Supabase (database)

## Project Conventions

### Code Style
- TypeScript on frontend; Python or TypeScript on backend per stack choice
- PT-BR for all user-facing strings; externalized via i18n from day one
- Server-side game mechanics; never delegate dice or wounds to LLM

### Architecture Patterns
- **Separation of concerns:** Rules engine (deterministic code) / Narrative (LLM) / Memory (database)
- **Signal protocol:** LLM emits tagged JSON signals (`[TESTE]`, `[IMAGEM]`, etc.); backend parses and executes
- **Four-layer memory:** Relational facts → pgvector semantic search → compressed LLM summaries → active session turn history
- **Two session modes:** EXPLORACAO (time-based) and COMBATE (turn-based)

### Testing Strategy
- Unit tests for WFRP rules engine (dice, combat, wounds, XP, progression)
- Integration tests for signal parsing and LLM loop (mocked LLM)
- API tests for character, campaign, and session lifecycle
- E2E test for main loop: create character → session → XP → progression

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

## External Dependencies

- LLM API (Anthropic Claude / DeepSeek) — model-agnostic adapter required
- Cloudflare Workers AI API — async image generation (FLUX.1 Schnell)
- Supabase — PostgreSQL + pgvector hosting
- Vercel — frontend hosting

## Reference Documents

- `Docs/README.md` — documentation index
- `Docs/product-brief.md` — product requirements and MVP scope
- `Docs/ux-spec.md` — UI/UX design spec (grimório palette, 9 screens)
- `Docs/prototype-gap-analysis.md` — Open Design prototype vs current frontend
- `Docs/session-flow.md` — Mermaid flows (session, combat, dice)
- `Docs/database-schema.md` — PostgreSQL + pgvector schema
- `Docs/development-order.md` — phased development order and OpenSpec sequencing
- `Docs/frontend-backend-split.md` — frontend vs backend responsibilities
- `Docs/gm-system-prompt.md` — GM persona and signal protocol
- `Docs/technical-research.md` — architecture and stack decisions

**UI prototype (Open Design):** `open-design/.od/projects/a37408fc-73d7-4e3e-8d6f-2367528ff373/`
