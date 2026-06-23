# Proposal: sqlite-only-database

**Data:** 2026-06-22  
**Status:** Draft  
**Relacionado:** `phase1-fixed-admin-login`, `phase1-controlled-release-readiness`, `add-local-db-alternatives` (arquivado — perfis postgres/supabase)

---

## Why

O projeto já roda integralmente em **SQLite** no dia a dia (`DATABASE_PROFILE=sqlite-dev`). Os perfis **PostgreSQL** e **Supabase** adicionam complexidade operacional (Docker, pgvector, Alembic condicional, dependências `asyncpg`/`pgvector`) sem uso real na fase 1.

Para deploy em VPS Debian ou teste controlado, um único arquivo `.db` é suficiente. A busca semântica já possui fallback **in-process** (`PythonSearchAdapter` + `simple_embedding`) — não depende de pgvector.

---

## What Changes

### Banco único: SQLite

| Antes | Depois |
|-------|--------|
| `sqlite-dev` \| `postgres` \| `supabase` | **SQLite apenas** |
| `pgvector` em PostgreSQL | Embeddings JSON + cosine similarity em Python |
| `docker-compose.yml` (Postgres) | **Removido** |
| `asyncpg`, `pgvector` em requirements | **Removidos** |
| `DATABASE_PROFILE` | Substituído por `DATABASE_URL` (default `sqlite+aiosqlite:///./wfrp_solo.db`) |

### Código backend

- `config.py` — remover perfis postgres/supabase e `is_postgres`
- `models.py` — embedding sempre `JSON` (remover import condicional pgvector)
- `memory.py` — remover `PgVectorSearchAdapter`; usar só `PythonSearchAdapter`
- `main.py` — remover diagnóstico PostgreSQL no `/health` e mensagens de erro pg
- `schema_patch.py` — remover branch postgres
- Alembic — simplificar migrations (sem `if dialect == postgresql`)
- `APP_ENV` — desacoplar de `DATABASE_PROFILE`; usar só `APP_ENV` explícito

### Infra e scripts

- Remover `docker-compose.yml`
- `check-dev.sh` — remover checagem porta 5432
- `run-tests.sh` — já usa sqlite; limpar env vars obsoletas

### Documentação

| Arquivo | Alteração |
|---------|-----------|
| `README.md` | Stack SQLite-only; remover tabela de perfis postgres |
| `.env.example` | Só `DATABASE_URL` sqlite |
| `Docs/architecture.md` | Diagrama sem PostgreSQL/pgvector |
| `Docs/database-schema.md` | Reescrever para SQLite (tipos, JSON embeddings) |
| `Docs/debian-server-install.md` | Remover seção PostgreSQL; persistir `wfrp_solo.db` |
| `Docs/mvp-validation-checklist.md` | Remover referências a postgres |
| `openspec/project.md` | Stack e deploy atualizados |

---

## Capabilities

### Modified Capabilities

- `dev-infrastructure`: banco SQLite único; docs sem Docker/Postgres
- `narrative-memory`: busca semântica via adapter Python (sem pgvector)

---

## Impact

| Área | Alterações |
|------|------------|
| Backend | config, models, memory, main, schema_patch, alembic |
| Deps | `-asyncpg`, `-pgvector` |
| Infra | delete docker-compose |
| Docs | 6+ arquivos |
| Testes | Remover/simplificar branches postgres; pytest verde |

---

## Non-Goals

- Migrar dados existentes de PostgreSQL para SQLite (sem usuários em prod PG)
- Otimizar SQLite para alta concorrência (MVP single-user/admin)
- Trocar `simple_embedding` por API de embeddings externa
- WAL mode tuning avançado (opcional follow-up)

---

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Perda de performance em busca semântica | MVP com poucos eventos; cosine em Python é aceitável |
| Backup em produção | Documentar cópia de `wfrp_solo.db` no guia Debian |
| Deploy com múltiplos workers uvicorn | Documentar 1 worker ou SQLite WAL (fase 1: 1 worker) |

---

## Open Questions (defaults assumidos)

| Questão | Decisão |
|---------|---------|
| Caminho default do DB | `./wfrp_solo.db` relativo ao cwd do backend |
| Override via env | `DATABASE_URL=sqlite+aiosqlite:///path/to/db` |
| Alembic em SQLite | Manter; `schema_patch` na subida para dev |
| `DATABASE_PROFILE` deprecado | Remover; warning se ainda setado |
