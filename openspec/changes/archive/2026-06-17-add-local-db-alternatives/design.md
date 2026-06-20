# Design: Alternativas de banco local

## Context

Dois erros consecutivos foram observados no Fedora:

1. `docker compose up -d` → `unix:///var/run/docker.sock: connect: no such file or directory` (Docker daemon ausente)
2. `uvicorn app.main:app` → `ConnectionResetError: [Errno 104] Connection reset by peer` em `asyncpg.connect` para `localhost:5432`

O segundo erro indica que o backend tenta PostgreSQL (via `DATABASE_URL=postgresql+asyncpg://wfrp:wfrp@localhost:5432/wfrp_solo`) mas **nenhum Postgres válido responde** na porta 5432. Causas comuns:
- Container Docker/Podman não subiu (passo 1 falhou)
- PostgreSQL nativo instalado mas serviço parado (`systemctl status postgresql`)
- Outro processo na porta 5432 que não fala protocolo PostgreSQL
- Tentativa de upgrade SSL quando o servidor local não suporta

O MVP foi implementado assumindo PostgreSQL + pgvector via Docker como único caminho documentado. Isso bloqueia dev local em máquinas onde:
- Docker não está instalado ou ativo
- O usuário prefere Podman (padrão em Fedora)
- O usuário quer começar rápido sem infraestrutura

## Goals / Non-Goals

**Goals:**
- Permitir `uvicorn` + frontend funcionando em < 5 minutos sem Docker
- Manter PostgreSQL + pgvector como caminho de produção e recomendado para memória semântica completa
- Documentar claramente trade-offs de cada perfil

**Non-Goals:**
- Substituir pgvector em produção
- Suportar MySQL ou outros bancos
- Gerenciar instalação automática de Docker/Podman no OS

## Decisions

### 1. Três perfis via `DATABASE_PROFILE`

| Perfil | URL exemplo | pgvector | Uso |
|--------|-------------|----------|-----|
| `sqlite-dev` | `sqlite+aiosqlite:///./wfrp_solo.db` | Não — fallback Python | Dev rápido, testes locais |
| `postgres` | `postgresql+asyncpg://...` | Sim | Docker, Podman, Postgres nativo |
| `supabase` | URL Supabase (PostgreSQL remoto) | Sim | Dev sem infra local |

`DATABASE_PROFILE` seleciona defaults; `DATABASE_URL` sempre pode sobrescrever.

### 2. Modelo de embeddings em dev

- **PostgreSQL:** coluna `Vector(384)` + busca pgvector (comportamento atual)
- **SQLite-dev:** coluna `JSON` com embedding serializado; busca via `simple_embedding()` + cosine similarity em Python (já existente em `memory.py`)

### 3. Startup condicional

```python
if is_postgres:
    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
await conn.run_sync(Base.metadata.create_all)
```

SQLite não executa `CREATE EXTENSION`.

### 4. Caminhos documentados para Fedora

**A) Podman (recomendado se Docker não disponível):**
```bash
sudo dnf install podman podman-compose
podman compose up -d
```

**B) Docker:**
```bash
sudo systemctl enable --now docker
sudo usermod -aG docker $USER  # relogar
docker compose up -d
```

**C) PostgreSQL nativo + pgvector:**
```bash
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
# criar user/db + instalar extensão pgvector
```

**D) SQLite-dev (sem instalação):**
```env
DATABASE_PROFILE=sqlite-dev
```

**E) Supabase (cloud):**
```env
DATABASE_PROFILE=supabase
DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[pass]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 5. Health check enriquecido

`GET /health` retorna `{ status, database_profile, database_ok }` para diagnóstico rápido.

### 6. Startup com erro acionável

Quando a conexão PostgreSQL falha no `lifespan`, o backend SHALL logar mensagem clara:

```
PostgreSQL inacessível em localhost:5432.
Opções: (1) docker/podman compose up -d  (2) DATABASE_PROFILE=sqlite-dev  (3) Supabase URL
```

Não SHALL exibir apenas stack trace de `ConnectionResetError` sem contexto.

### 7. Diagnóstico rápido da porta 5432

Documentar no README:

```bash
ss -tlnp | grep 5432          # algo escutando?
podman compose ps             # container up?
systemctl status postgresql   # postgres nativo?
```

Se nada responder corretamente → usar `sqlite-dev` imediatamente.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| SQLite diverge de produção | Documentar; testes de integração rodam em Postgres |
| Busca semântica mais lenta em SQLite | Aceitável para dev; limit N eventos |
| Confusão entre perfis | `.env.example` com exemplos comentados por perfil |

## Migration Plan

1. Adicionar `aiosqlite` às dependências
2. Refatorar model para tipo de embedding condicional ou tabela sem Vector em SQLite
3. Atualizar README com seção "Escolha seu setup"
4. Desenvolvedores existentes com Docker: nenhuma mudança (default `postgres`)

## Open Questions

- **Fechada:** Default de novos clones será `sqlite-dev`; `.env.example` documenta upgrade para `postgres` quando Docker/Podman estiver disponível.
