# Instalação em servidor Linux (Debian)

Guia passo a passo para implantar o **WFRP Solo** em um servidor **Debian 12** (ou Ubuntu 22.04+) com **Docker Compose**, **SQLite** persistido no disco do host e **nginx** como reverse proxy.

**Cenário:** teste controlado ou produção self-hosted (alternativa a Vercel + Railway).

---

## Pré-requisitos

| Item | Versão mínima |
|------|----------------|
| SO | Debian 12 / Ubuntu 22.04 LTS |
| RAM | 2 GB (4 GB recomendado com LLM ativo) |
| Disco | 10 GB livres |
| Docker | Engine 24+ e Compose v2 |
| Domínio | Opcional (HTTPS recomendado) |
| Portas | 80, 443 (nginx no host) |

Contas/API keys necessárias:

- Chave **DeepSeek** (`DEEPSEEK_API_KEY`)
- **ADMIN_PASSWORD** (fase 1 — login fixo; mín. 8 caracteres)
- Servidor **SMTP** (somente se `AUTH_MODE=multi_user`)
- (Opcional) **Cloudflare Workers AI** para ilustrações

---

## 1. Preparar o sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl nginx certbot python3-certbot-nginx sqlite3
```

### Docker Engine + Compose

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
# Relogue ou: newgrp docker
docker compose version
```

### Diretório de dados (SQLite no host)

O banco **não fica dentro do container** — é um bind mount para um path no servidor. Assim você pode fazer backup, inspecionar com `sqlite3` e trocar containers sem perder dados.

```bash
sudo mkdir -p /opt/wfrp-solo/data /opt/wfrp-solo/app
sudo chown -R "$USER":"$USER" /opt/wfrp-solo
```

Arquivo esperado após a primeira subida: `/opt/wfrp-solo/data/wfrp_solo.db`

---

## 2. Clonar o repositório

```bash
cd /opt/wfrp-solo
git clone https://github.com/SEU_USUARIO/SoloRPG.git app
cd app
```

Substitua a URL pelo repositório real.

---

## 3. Configurar ambiente

```bash
cp .env.docker.example .env
```

Edite `.env` na **raiz do repo** (`/opt/wfrp-solo/app/.env`):

```env
WFRP_DATA_DIR=/opt/wfrp-solo/data
BACKEND_BIND=127.0.0.1:8000
FRONTEND_BIND=127.0.0.1:3000

APP_ENV=production

JWT_SECRET=GERE_STRING_ALEATORIA_32_CARACTERES_OU_MAIS
JWT_EXPIRE_DAYS=7

AUTH_MODE=fixed_admin
ADMIN_PASSWORD=SENHA_FORTE_MIN_8_CHARS

EMAIL_PROVIDER=mock

LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sua-chave-deepseek
LLM_MODEL=deepseek-chat

CORS_ORIGINS=https://rpg.seudominio.com
API_BASE_URL=https://api.rpg.seudominio.com

ENABLE_CUSTOM_CHARGEN=false

NEXT_PUBLIC_API_URL=https://api.rpg.seudominio.com
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN=false
```

Gerar `JWT_SECRET`:

```bash
openssl rand -hex 32
```

> **Nota:** `DATABASE_URL` é definido no `docker-compose.yml` como `sqlite+aiosqlite:////data/wfrp_solo.db` (path `/data` dentro do container = `WFRP_DATA_DIR` no host). Use **1 worker** uvicorn (SQLite write lock).

---

## 4. Subir com Docker Compose

```bash
cd /opt/wfrp-solo/app
mkdir -p /opt/wfrp-solo/data
docker compose up -d --build
docker compose ps
docker compose logs -f backend   # Ctrl+C para sair
```

Verificar saúde:

```bash
curl -s http://127.0.0.1:8000/health | jq .
# {"status":"ok","database_ok":true,...}

ls -la /opt/wfrp-solo/data/
# wfrp_solo.db criado no host
```

Comandos úteis:

```bash
docker compose restart backend frontend
docker compose down          # para containers; dados em /opt/wfrp-solo/data permanecem
docker compose up -d --build # rebuild após git pull
```

---

## 5. nginx (reverse proxy no host)

Substitua `rpg.seudominio.com` e `api.rpg.seudominio.com` pelos seus domínios. Os containers escutam só em `127.0.0.1`; nginx expõe 80/443.

```bash
sudo tee /etc/nginx/sites-available/wfrp-solo <<'NGINX'
server {
    listen 80;
    server_name rpg.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}

server {
    listen 80;
    server_name api.rpg.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/wfrp-solo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d rpg.seudominio.com -d api.rpg.seudominio.com
```

Atualize `CORS_ORIGINS`, `API_BASE_URL` e `NEXT_PUBLIC_API_URL` para `https://`, depois **rebuild do frontend** (variáveis `NEXT_PUBLIC_*` são de build-time):

```bash
cd /opt/wfrp-solo/app
docker compose up -d --build frontend
```

---

## 6. Backup do banco

O arquivo está no host em `WFRP_DATA_DIR` (ex.: `/opt/wfrp-solo/data/wfrp_solo.db`).

```bash
# Com backend parado (recomendado):
cd /opt/wfrp-solo/app
docker compose stop backend
cp /opt/wfrp-solo/data/wfrp_solo.db "/opt/wfrp-solo/data/wfrp_solo.db.$(date +%Y%m%d)"
docker compose start backend
```

Inspeção manual:

```bash
sqlite3 /opt/wfrp-solo/data/wfrp_solo.db ".tables"
```

Agende cron diário se necessário.

---

## 7. Smoke test pós-deploy

1. Abra `https://rpg.seudominio.com/login`
2. Entre com a senha definida em `ADMIN_PASSWORD` → home com personagem starter
3. `/register` redireciona para login; `POST /api/auth/register` retorna 404
4. Escolha pré-gerado em `/character` → inicie campanha → 1 sessão
5. Troque `ADMIN_PASSWORD` no `.env`, `docker compose restart backend` e confirme login com a nova senha

```bash
curl -s https://api.rpg.seudominio.com/health
```

---

## 8. Atualizações

```bash
cd /opt/wfrp-solo/app
git pull
docker compose up -d --build
```

Se alterou `NEXT_PUBLIC_*`, o rebuild do frontend é obrigatório (já incluído em `--build`).

---

## 9. Troubleshooting

| Problema | Solução |
|----------|---------|
| Backend não sobe | `docker compose logs backend` — verificar `JWT_SECRET` e `ADMIN_PASSWORD` |
| `database_ok: false` | Permissões em `WFRP_DATA_DIR`; volume montado em `/data` |
| CORS error no browser | `CORS_ORIGINS` deve bater com URL do frontend (com `https://`) |
| Frontend chama API errada | Rebuild frontend após mudar `NEXT_PUBLIC_API_URL` |
| E-mail não chega | Testar SMTP com `swaks` ou logs do provider (`multi_user` only) |
| 403 em wizard | Esperado — `ENABLE_CUSTOM_CHARGEN=false` na fase 1 |
| Imagens não carregam | Configurar Cloudflare ou aceitar placeholder |

---

## 10. Desenvolvimento local com Docker

Na raiz do repo (sem nginx):

```bash
cp .env.docker.example .env
# Ajuste ADMIN_PASSWORD, LLM_PROVIDER=mock, etc.
# WFRP_DATA_DIR=./data (padrão)

docker compose up --build
```

Acesse **http://127.0.0.1:3000** (frontend) e **http://127.0.0.1:8000/health** (API). O banco fica em `./data/wfrp_solo.db` no seu workspace.

---

## Alternativa: deploy gerenciado (sem Docker)

| Componente | Serviço |
|------------|---------|
| Frontend | Vercel (`frontend/`) |
| Backend | Railway ou Fly.io (`backend/`) + volume persistente para `.db` |

Variáveis de ambiente: ver `.env.example`. Ver também o [README](../README.md) §Deploy.

---

## Alternativa: instalação nativa (systemd)

Se preferir **sem containers**, instale Python 3.11+, Node 20+, venv, systemd e nginx manualmente. O banco continua em `/opt/wfrp-solo/data/wfrp_solo.db` com `DATABASE_URL=sqlite+aiosqlite:////opt/wfrp-solo/data/wfrp_solo.db`. Consulte commits anteriores deste guia ou a documentação em `README.md` §Instalação local.

---

## Referências

- [Arquitetura](architecture.md)
- [Checklist de validação MVP](mvp-validation-checklist.md)
- [Schema do banco](database-schema.md)
- [`docker-compose.yml`](../docker-compose.yml) e [`.env.docker.example`](../.env.docker.example)