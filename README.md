# WFRP Solo

Aplicação web de RPG solo onde uma LLM atua como GM sintético para campanhas WFRP4e.

## Stack

- **Frontend:** Next.js 14, TailwindCSS, TypeScript
- **Backend:** FastAPI, SQLAlchemy, SQLite (dev) ou PostgreSQL + pgvector (prod)
- **LLM:** DeepSeek por padrão (`deepseek-chat`); adapter suporta mock / Claude

## Escolha seu setup

| Perfil | Quando usar | Comando |
|--------|-------------|---------|
| **sqlite-dev** (default) | Começar rápido, sem Docker | `DATABASE_PROFILE=sqlite-dev` |
| **postgres** | Docker/Podman local | `docker compose up -d` |
| **supabase** | Banco remoto | `DATABASE_URL` do Supabase |

Verifique pré-requisitos:

```bash
chmod +x scripts/check-dev.sh
./scripts/check-dev.sh
```

## Setup Local (sqlite-dev — recomendado)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # obrigatório antes de uvicorn/pytest sem caminho completo
pip install -r requirements.txt
cp ../.env.example .env
# Edite .env: DEEPSEEK_API_KEY=sua-chave (ou LLM_PROVIDER=mock para testes)
DATABASE_PROFILE=sqlite-dev uvicorn app.main:app --reload --port 8000
```

Sem ativar o venv, use o caminho explícito:

```bash
cd backend && .venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

Acesse http://localhost:3000

### Setup com PostgreSQL (Docker ou Podman)

```bash
# Docker
sudo systemctl enable --now docker
docker compose up -d

# Fedora sem Docker — Podman
sudo dnf install podman podman-compose
podman compose up -d
```

No `backend/.env`:

```env
DATABASE_PROFILE=postgres
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sua-chave
```

## Troubleshooting

| Erro | Solução |
|------|---------|
| `docker.sock: no such file` | Use `podman compose up -d` ou `DATABASE_PROFILE=sqlite-dev` |
| `Connection reset by peer` em `:5432` | Postgres não está rodando — `ss -tlnp \| grep 5432`, ou use sqlite-dev |
| Backend não sobe | `./scripts/check-dev.sh` |
| Narrativa mock em vez de DeepSeek | Confirme `LLM_PROVIDER=deepseek` e `DEEPSEEK_API_KEY` no `.env` |
| Colunas novas não aparecem no sqlite-dev | Apague `backend/wfrp_solo.db` e reinicie o backend (ou deixe o `schema_patch` na subida aplicar `ALTER TABLE`) |

Diagnóstico rápido:

```bash
curl http://localhost:8000/health
# {"status":"ok","database_profile":"sqlite-dev","database_ok":true,"llm_provider":"deepseek"}
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `DATABASE_PROFILE` | `sqlite-dev` (default), `postgres`, ou `supabase` |
| `DATABASE_URL` | Sobrescreve URL do perfil (obrigatório para supabase) |
| `LLM_PROVIDER` | `deepseek` (default), `mock`, ou `anthropic` |
| `LLM_MODEL` | `deepseek-chat` (default) |
| `DEEPSEEK_API_KEY` | Chave API DeepSeek |
| `ANTHROPIC_API_KEY` | Chave API Anthropic |
| `CLOUDFLARE_ACCOUNT_ID` | Account ID do Cloudflare (Workers AI) |
| `CLOUDFLARE_API_TOKEN` | Token com permissão Workers AI; sem credenciais usa placeholder temático |
| `CLOUDFLARE_AI_MODEL` | Modelo Workers AI (default: `@cf/black-forest-labs/flux-1-schnell`) |
| `API_BASE_URL` | URL pública do backend para links de imagens (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_API_URL` | URL do backend (default: http://localhost:8000) |

## Testes

```bash
# Suite local (pytest + build frontend)
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh

# Incluir E2E Playwright (sobe backend mock + Next em portas de teste)
cd frontend && npm install && npx playwright install chromium
RUN_E2E=1 ./scripts/run-tests.sh

# Apenas backend
cd backend && source .venv/bin/activate && pytest tests/ -q
```

O E2E cobre: pré-gerado → campanha → sessão → rolagem → recap (`frontend/e2e/game-loop.spec.ts`).  
Validação manual de campanha 3–5 sessões com DeepSeek: [`Docs/mvp-validation-checklist.md`](Docs/mvp-validation-checklist.md).

## Deploy

- **Frontend:** Vercel (`frontend/`)
- **Backend:** Railway ou Fly.io (`backend/`)
- **Banco:** Supabase com extensão pgvector

## Loop de Jogo

1. Criar ou selecionar personagem (pré-gerado ou customizado)
2. Iniciar campanha → primeira sessão gera cenário via LLM
3. Jogar sessão via texto livre (timer visível, pausável)
4. Rolagens server-side com animação na UI
5. Fim de sessão → resumo + XP → progressão entre sessões

## Documentação

Índice completo: **[Docs/README.md](Docs/README.md)**

### Guias de desenvolvimento

- [Ordem de desenvolvimento](Docs/development-order.md) — fases, dependências e propostas OpenSpec
- [Frontend vs Backend](Docs/frontend-backend-split.md) — responsabilidades, pastas e APIs
- [Gap protótipo ↔ código](Docs/prototype-gap-analysis.md) — análise Open Design vs frontend atual

### Referência do produto

- [UX spec](Docs/ux-spec.md) — design visual e comportamental
- [Session flow](Docs/session-flow.md) — fluxos Mermaid
- [Database schema](Docs/database-schema.md) — PostgreSQL + pgvector
- [Product brief](Docs/product-brief.md)
- [System prompt GM](Docs/gm-system-prompt.md)
- [Pesquisa técnica](Docs/technical-research.md)

### Specs

- OpenSpec (MVP): `openspec/changes/add-wfrp-solo-mvp/`
- Propostas pendentes: `openspec/changes/` (ver [ordem de desenvolvimento](Docs/development-order.md))
