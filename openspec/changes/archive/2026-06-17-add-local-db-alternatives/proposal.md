# Change: Alternativas de banco de dados para desenvolvimento local

## Why

O setup atual exige `docker compose up -d` para PostgreSQL + pgvector. Dois erros bloqueiam o dev local no Fedora:

1. **Docker indisponível:** `unix:///var/run/docker.sock: connect: no such file or directory`
2. **PostgreSQL inacessível:** `uvicorn` falha no startup com `ConnectionResetError: [Errno 104] Connection reset by peer` ao conectar em `localhost:5432` — ocorre quando o container/serviço Postgres não está rodando, a porta está ocupada por outro processo, ou o handshake SSL falha.

Em ambos os casos, o backend aborta em `lifespan` (`CREATE EXTENSION vector` + `create_all`) sem mensagem acionável, mesmo com LLM e frontend já configurados.

## What Changes

- Introduz perfis de banco configuráveis via env (`postgres`, `sqlite-dev`, `supabase`)
- Perfil `sqlite-dev`: zero dependências externas para desenvolvimento local imediato
- Perfil `postgres`: Docker, Podman ou PostgreSQL nativo com pgvector
- Perfil `supabase`: URL remota sem infra local
- Startup condicional: extensão pgvector só em PostgreSQL; busca semântica com fallback Python em dev
- Documentação de setup para Fedora (Podman, PostgreSQL nativo, Supabase)
- Script de verificação de pré-requisitos (`scripts/check-dev.sh`)
- Mensagens de erro de startup acionáveis quando PostgreSQL estiver inacessível
- Default de novos clones: `DATABASE_PROFILE=sqlite-dev` (PostgreSQL continua recomendado para prod)

## Impact

- Affected specs: `dev-infrastructure` (nova), `narrative-memory` (modificada — fallback sem pgvector)
- Affected code: `backend/app/config.py`, `backend/app/main.py`, `backend/app/db/models.py`, `backend/app/services/memory.py`, `README.md`, `.env.example`, `docker-compose.yml` (comentários Podman)
- Não altera comportamento de produção (PostgreSQL + pgvector permanece o caminho recomendado)
