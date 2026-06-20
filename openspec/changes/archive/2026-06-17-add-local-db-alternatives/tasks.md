# Tasks: Alternativas de banco local

## 1. Configuração de perfis

- [x] 1.1 Adicionar `DATABASE_PROFILE` (`sqlite-dev` | `postgres` | `supabase`) em `config.py`
- [x] 1.2 Resolver `DATABASE_URL` automaticamente por perfil quando URL não definida explicitamente
- [x] 1.3 Atualizar `.env.example` com exemplos comentados para cada perfil (default: `sqlite-dev`)

## 2. Backend — compatibilidade SQLite

- [x] 2.1 Adicionar `aiosqlite` ao `requirements.txt`
- [x] 2.2 Tornar coluna de embedding compatível (Vector em Postgres, JSON em SQLite)
- [x] 2.3 Startup condicional: pular `CREATE EXTENSION vector` fora de PostgreSQL
- [x] 2.4 Garantir que `create_all` funciona em ambos os backends

## 3. Memória semântica — fallback

- [x] 3.1 Extrair busca por similaridade para adapter (`PgVectorSearch` / `PythonSearch`)
- [x] 3.2 Usar fallback Python em `sqlite-dev`; pgvector em `postgres`/`supabase`
- [x] 3.3 Testes unitários para ambos os adapters de busca

## 4. Diagnóstico e scripts

- [x] 4.1 Enriquecer `GET /health` com profile e status de conexão
- [x] 4.2 Criar `scripts/check-dev.sh` (Python, Node, DB reachable, LLM key opcional)
- [x] 4.3 Capturar `ConnectionResetError`/falhas asyncpg no lifespan com mensagem acionável (host, porta, opções)
- [x] 4.4 Documentar diagnóstico de porta 5432 (`ss`, `podman compose ps`, `systemctl status postgresql`)

## 5. Documentação

- [x] 5.1 Atualizar README: seção "Escolha seu setup" (SQLite / Docker / Podman / Postgres nativo / Supabase)
- [x] 5.2 Documentar fix do erro Docker no Fedora (`systemctl start docker` vs Podman)
- [x] 5.3 Adicionar troubleshooting com mensagens de erro comuns

## 6. Validação

- [x] 6.1 Subir backend com `DATABASE_PROFILE=sqlite-dev` sem Docker
- [x] 6.2 Verificar loop: criar personagem → campanha → sessão com SQLite
- [x] 6.3 Confirmar que perfil `postgres` + `docker compose up -d` continua funcionando
