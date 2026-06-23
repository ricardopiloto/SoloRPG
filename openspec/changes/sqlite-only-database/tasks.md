# Tasks: sqlite-only-database

## 1. Config e conexão

- [x] 1.1 Remover `database_profile`, perfis postgres/supabase, `is_postgres` de `config.py`
- [x] 1.2 `database_url` default `sqlite+aiosqlite:///./wfrp_solo.db`; validar prefixo sqlite
- [x] 1.3 Desacoplar `effective_app_env` de perfil de banco (só `APP_ENV`)
- [x] 1.4 Atualizar `.env.example` — remover `DATABASE_PROFILE`, postgres, supabase

## 2. Backend código

- [x] 2.1 `models.py` — embedding sempre JSON; remover import pgvector
- [x] 2.2 `memory.py` — remover `PgVectorSearchAdapter`; `get_semantic_search()` → Python only
- [x] 2.3 `main.py` — health sem branch postgres; remover hints porta 5432
- [x] 2.4 `schema_patch.py` — remover branch postgres
- [x] 2.5 Alembic versions — remover guards `dialect.name == postgresql` onde seguro
- [x] 2.6 `requirements.txt` — remover `asyncpg`, `pgvector`

## 3. Infra

- [x] 3.1 Remover `docker-compose.yml`
- [x] 3.2 `scripts/check-dev.sh` — só sqlite, sem checagem 5432
- [x] 3.3 `scripts/run-tests.sh` — `DATABASE_URL` sqlite, sem `DATABASE_PROFILE`

## 4. Testes

- [x] 4.1 Atualizar `conftest.py` e testes que setam `DATABASE_PROFILE`
- [x] 4.2 `pytest tests/ -q` verde
- [x] 4.3 Confirmar `test_memory_search.py` cobre busca semântica

## 5. Documentação

- [x] 5.1 `README.md` — stack SQLite-only, setup simplificado, troubleshooting
- [x] 5.2 `Docs/architecture.md` — diagrama e tabela de integrações
- [x] 5.3 `Docs/database-schema.md` — reescrever para SQLite
- [x] 5.4 `Docs/debian-server-install.md` — remover PostgreSQL; path persistente do .db
- [x] 5.5 `Docs/mvp-validation-checklist.md`, `Docs/product-brief.md` (refs PG)
- [x] 5.6 `openspec/project.md` — tech stack e external deps
- [x] 5.7 `Docs/README.md` — descrição database-schema atualizada

## 6. Validação

- [x] 6.1 Subir backend sem Docker → `/health` ok
- [x] 6.2 Campanha com turnos → memória semântica retorna eventos
- [x] 6.3 `npm run build` + E2E (se aplicável) verdes
