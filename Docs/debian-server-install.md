# Instalação em servidor Linux (Debian)

Guia passo a passo para implantar o **WFRP Solo** em um servidor **Debian 12** (ou Ubuntu 22.04+) com **SQLite**, backend FastAPI e frontend Next.js atrás de nginx.

**Cenário:** teste controlado ou produção self-hosted (alternativa a Vercel + Railway).

---

## Pré-requisitos

| Item | Versão mínima |
|------|----------------|
| SO | Debian 12 / Ubuntu 22.04 LTS |
| RAM | 2 GB (4 GB recomendado com LLM ativo) |
| Disco | 10 GB livres |
| Domínio | Opcional (HTTPS recomendado) |
| Portas | 80, 443 (nginx) |

Contas/API keys necessárias:

- Chave **DeepSeek** (`DEEPSEEK_API_KEY`)
- **ADMIN_PASSWORD** (fase 1 — login fixo; mín. 8 caracteres)
- Servidor **SMTP** (somente se `AUTH_MODE=multi_user`)
- (Opcional) **Cloudflare Workers AI** para ilustrações

---

## 1. Preparar o sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl build-essential nginx certbot python3-certbot-nginx \
  python3 python3-venv python3-pip sqlite3
```

### Node.js 20 (via NodeSource)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v   # v20.x
```

### Usuário de serviço e diretório de dados

```bash
sudo useradd -r -m -d /opt/wfrp-solo -s /bin/bash wfrp
sudo mkdir -p /opt/wfrp-solo/data
sudo chown -R wfrp:wfrp /opt/wfrp-solo
```

O banco SQLite ficará em `/opt/wfrp-solo/data/wfrp_solo.db` (persistente entre deploys).

---

## 2. Clonar o repositório

```bash
sudo -u wfrp bash -c '
  cd /opt/wfrp-solo
  git clone https://github.com/SEU_USUARIO/SoloRPG.git app
  cd app
'
```

Substitua a URL pelo repositório real.

---

## 3. Backend (FastAPI)

```bash
sudo -u wfrp bash -c '
  cd /opt/wfrp-solo/app/backend
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  cp ../.env.example .env
'
```

Edite `/opt/wfrp-solo/app/backend/.env`:

```env
APP_ENV=production
DATABASE_URL=sqlite+aiosqlite:////opt/wfrp-solo/data/wfrp_solo.db

JWT_SECRET=GERE_STRING_ALEATORIA_32_CARACTERES_OU_MAIS
JWT_EXPIRE_DAYS=7

AUTH_MODE=fixed_admin
ADMIN_PASSWORD=SENHA_FORTE_MIN_8_CHARS

EMAIL_PROVIDER=mock
# Fase 2 (multi_user): EMAIL_PROVIDER=smtp + SMTP_* abaixo
# SMTP_HOST=smtp.seudominio.com
# SMTP_PORT=587
# SMTP_USER=noreply@seudominio.com
# SMTP_PASSWORD=senha_smtp
# SMTP_FROM=noreply@seudominio.com
# SMTP_USE_TLS=true

LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sua-chave-deepseek
LLM_MODEL=deepseek-chat

CORS_ORIGINS=https://rpg.seudominio.com
API_BASE_URL=https://api.rpg.seudominio.com

ENABLE_CUSTOM_CHARGEN=false

# Opcional — imagens
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
```

Gerar `JWT_SECRET`:

```bash
openssl rand -hex 32
```

> **Nota:** use **1 worker** uvicorn (SQLite write lock). Schema criado automaticamente na primeira subida.

### Systemd — backend

```bash
sudo tee /etc/systemd/system/wfrp-backend.service <<'UNIT'
[Unit]
Description=WFRP Solo API
After=network.target

[Service]
User=wfrp
Group=wfrp
WorkingDirectory=/opt/wfrp-solo/app/backend
EnvironmentFile=/opt/wfrp-solo/app/backend/.env
ExecStart=/opt/wfrp-solo/app/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now wfrp-backend
```

Verificar:

```bash
curl -s http://127.0.0.1:8000/health | jq .
# {"status":"ok","database_ok":true,...}
```

---

## 4. Frontend (Next.js)

```bash
sudo -u wfrp bash -c '
  cd /opt/wfrp-solo/app/frontend
  npm ci
  npm run prepare:dice
'
```

Crie `/opt/wfrp-solo/app/frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=https://api.rpg.seudominio.com
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN=false
```

Build de produção:

```bash
sudo -u wfrp bash -c '
  cd /opt/wfrp-solo/app/frontend
  npm run build
'
```

### Systemd — frontend

```bash
sudo tee /etc/systemd/system/wfrp-frontend.service <<'UNIT'
[Unit]
Description=WFRP Solo Frontend
After=network.target wfrp-backend.service

[Service]
User=wfrp
Group=wfrp
WorkingDirectory=/opt/wfrp-solo/app/frontend
EnvironmentFile=/opt/wfrp-solo/app/frontend/.env.local
ExecStart=/usr/bin/npm run start -- -p 3000 -H 127.0.0.1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl enable --now wfrp-frontend
```

---

## 5. nginx (reverse proxy)

Substitua `rpg.seudominio.com` e `api.rpg.seudominio.com` pelos seus domínios.

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

Atualize `CORS_ORIGINS` e `NEXT_PUBLIC_API_URL` para `https://`.

---

## 6. Backup do banco

```bash
# Com backend parado (recomendado):
sudo systemctl stop wfrp-backend
sudo -u wfrp cp /opt/wfrp-solo/data/wfrp_solo.db /opt/wfrp-solo/data/wfrp_solo.db.$(date +%Y%m%d)
sudo systemctl start wfrp-backend
```

Agende cron diário se necessário.

---

## 7. Smoke test pós-deploy

1. Abra `https://rpg.seudominio.com/login`
2. Entre com a senha definida em `ADMIN_PASSWORD` → home com personagem starter
3. `/register` redireciona para login; `POST /api/auth/register` retorna 404
4. Escolha pré-gerado em `/character` → inicie campanha → 1 sessão
5. Troque `ADMIN_PASSWORD` no `.env`, reinicie o backend e confirme login com a nova senha

```bash
curl -s https://api.rpg.seudominio.com/health
```

---

## 8. Atualizações

```bash
sudo -u wfrp bash -c '
  cd /opt/wfrp-solo/app
  git pull
  cd backend && .venv/bin/pip install -r requirements.txt
  cd ../frontend && npm ci && npm run build
'
sudo systemctl restart wfrp-backend wfrp-frontend
```

---

## 9. Troubleshooting

| Problema | Solução |
|----------|---------|
| Backend não sobe | `journalctl -u wfrp-backend -n 50` — verificar `JWT_SECRET` e `ADMIN_PASSWORD` |
| `database_ok: false` | Permissões em `/opt/wfrp-solo/data/`; path em `DATABASE_URL` |
| CORS error no browser | `CORS_ORIGINS` deve bater com URL do frontend (com `https://`) |
| E-mail não chega | Testar SMTP com `swaks` ou logs do provider |
| 403 em wizard | Esperado — `ENABLE_CUSTOM_CHARGEN=false` na fase 1 |
| Imagens não carregam | Configurar Cloudflare ou aceitar placeholder |

---

## Alternativa: deploy gerenciado

| Componente | Serviço |
|------------|---------|
| Frontend | Vercel (`frontend/`) |
| Backend | Railway ou Fly.io (`backend/`) + volume persistente para `.db` |

Variáveis de ambiente são as mesmas da seção 3. Ver também o [README](../README.md) §Deploy.

---

## Referências

- [Arquitetura](architecture.md)
- [Checklist de validação MVP](mvp-validation-checklist.md)
- [Schema do banco](database-schema.md)
