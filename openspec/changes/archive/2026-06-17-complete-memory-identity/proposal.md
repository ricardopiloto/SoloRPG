# Change: Memória semântica e identidade completas

## Why

Gaps: pgvector não usado em queries SQL; `social_perception` nunca atualizada; Fortune Points sem regras de gasto; Alembic ausente; `SessionTurn` table unused.

## What Changes

- Busca pgvector real em PostgreSQL (fallback Python em sqlite-dev via `add-local-db-alternatives`)
- Atualizar `social_perception` em `[FIM_SESSAO]`
- Regras Fortune Points
- Alembic migrations
- Opcional: persistir SessionTurn records

## Impact

- Affected specs: `narrative-memory`, `identity-layers`, `wfrp-rules-engine`
- Depends on: `add-local-db-alternatives` para perfil sqlite-dev
