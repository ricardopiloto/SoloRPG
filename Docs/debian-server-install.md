# Deploy em servidor Linux (Ubuntu / Debian)

Guia passo a passo para implantar o **WFRP Solo** em um servidor **Ubuntu 24.04/26.04** (ou Debian 12) com **Docker Compose**, **SQLite persistido fora do repo**, **Caddy** como reverse proxy e **Cloudflare Tunnel** para TLS e roteamento externo.

**Cenário de referência usado neste guia:**

| Item | Valor |
|------|-------|
| Domínio (frontend) | `solorpg.1nodado.com.br` |
| Domínio (API) | `api.solorpg.1nodado.com.br` |
| Diretório do repo | `/opt/apps/solorpg/app` |
| Banco de dados | `/opt/apps/solorpg/data/wfrp_solo.db` |

> Ajuste os paths e domínios conforme o seu ambiente.

---

## Por que o banco fica fora do repo?

```
/opt/apps/solorpg/
├── data/    ← SQLite aqui — NUNCA apagado com docker compose down
└── app/     ← git clone (docker-compose.yml, Dockerfiles, etc.)
```

O `docker-compose.yml` monta `/opt/apps/solorpg/data` dentro do container como `/data` (bind mount). Se você:

- Fizer `docker compose down` → containers somem, dados intactos
- Fizer `docker compose down -v` → mesma coisa (não há volume nomeado)
- Deletar `/opt/apps/solorpg/app/` → dados em `data/` permanecem
- Fizer rollback do repo → banco não é afetado

---

## Pré-requisitos

| Item | Versão mínima |
|------|----------------|
| SO | Ubuntu 22.04+ / Debian 12 |
| RAM | 2 GB (4 GB recomendado com LLM ativo) |
| Disco | 10 GB livres |
| Docker | Engine 24+ e Compose v2 |
| Domínio | Dois registros DNS apontando para o IP do servidor |
| Portas | Somente 80 local (Caddy); Cloudflare Tunnel expõe HTTPS externamente |

Contas/chaves necessárias:

- Chave **DeepSeek** (`DEEPSEEK_API_KEY`)
- **ADMIN_PASSWORD** (fase 1 — login fixo; mín. 8 caracteres)
- Servidor **SMTP** (somente se `AUTH_MODE=multi_user`)
- (Opcional) **Cloudflare Workers AI** para ilustrações

---

## 1. Preparar o sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git sqlite3
```

> **Caddy e Docker** já estão instalados no servidor. Confirme que o usuário `adminvtt` está no grupo `docker`:
>
> ```bash
> groups adminvtt          # deve listar "docker"
> docker compose version   # deve mostrar v2.x
> ```
>
> Se `docker` não aparecer nos grupos:
>
> ```bash
> sudo usermod -aG docker adminvtt
> newgrp docker
> ```

### Estrutura de diretórios

```bash
# Cria repo + dados SEPARADOS — chave para persistência do banco
sudo mkdir -p /opt/apps/solorpg/data /opt/apps/solorpg/app
sudo chown -R adminvtt:adminvtt /opt/apps/solorpg
```

---

## 2. Clonar o repositório

```bash
cd /opt/apps/solorpg
git clone https://github.com/SEU_USUARIO/SoloRPG.git app
cd app
```

> Substitua pela URL real do seu repositório.

---

## 3. Configurar o ambiente

```bash
cp .env.docker.example .env
nano .env          # ou vim, ou qualquer editor
```

Valores para o cenário de referência:

```env
# Onde o banco fica no HOST
WFRP_DATA_DIR=/opt/apps/solorpg/data

# Portas internas (Caddy faz o proxy externo)
BACKEND_BIND=127.0.0.1:8000
FRONTEND_BIND=127.0.0.1:3000

APP_ENV=production

# Gere com: openssl rand -hex 32
JWT_SECRET=COLE_STRING_ALEATORIA_AQUI
JWT_EXPIRE_DAYS=7

AUTH_MODE=fixed_admin
ADMIN_PASSWORD=SENHA_FORTE_MIN_8_CHARS

EMAIL_PROVIDER=mock

LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sua-chave-deepseek
LLM_MODEL=deepseek-chat

API_BASE_URL=https://api.solorpg.1nodado.com.br
CORS_ORIGINS=https://solorpg.1nodado.com.br

ENABLE_CUSTOM_CHARGEN=false

# Variáveis de build-time do Next.js
NEXT_PUBLIC_API_URL=https://api.solorpg.1nodado.com.br
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN=false
```

Gerar JWT_SECRET:

```bash
openssl rand -hex 32
```

> **Nota:** `DATABASE_URL` é definido automaticamente no `docker-compose.yml` como
> `sqlite+aiosqlite:////data/wfrp_solo.db` — o path `/data` dentro do container
> corresponde a `WFRP_DATA_DIR` no host. Não altere isso.

---

## 4. Subir com Docker Compose

```bash
cd /opt/apps/solorpg/app

# Confirma que o diretório de dados existe
ls -la /opt/apps/solorpg/data

# Build + start
docker compose up -d --build

# Acompanhar logs
docker compose logs -f backend    # Ctrl+C para sair
docker compose ps                 # deve mostrar ambos "running"
```

Verificar saúde:

```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
# {"status":"ok","database_ok":true,...}

ls -la /opt/apps/solorpg/data/
# wfrp_solo.db criado no HOST pelo container
```

Comandos úteis:

```bash
# Parar/iniciar (dados intactos)
docker compose stop
docker compose start

# Parar e remover containers (dados intactos)
docker compose down

# Rebuild após git pull
git pull
docker compose up -d --build

# Rebuild só do frontend (após mudar NEXT_PUBLIC_*)
docker compose up -d --build frontend
```

---

## 5. Cloudflare Tunnel + DNS

### Como funciona o fluxo

```
Usuário (HTTPS) → Cloudflare → cloudflared (túnel) → localhost:80 (Caddy) → containers
```

- O **TLS é gerenciado pelo Cloudflare** — o servidor nunca vê HTTPS
- O Caddy recebe HTTP simples na porta 80 e roteia pelo `Host` header
- **Não é necessário** registrar A/AAAA no DNS — o tunnel usa CNAME automático

### 5a. Adicionar os CNAMEs no painel Cloudflare

No DNS do domínio `1nodado.com.br`, crie dois registros CNAME apontando para o tunnel:

| Tipo | Nome | Destino | Proxy |
|------|------|---------|-------|
| CNAME | `solorpg` | `<tunnel-id>.cfargotunnel.com` | ✅ Proxied |
| CNAME | `api.solorpg` | `<tunnel-id>.cfargotunnel.com` | ✅ Proxied |

Substitua `<tunnel-id>` pelo seu: `245bcb96-a72e-4df3-9bad-74d6d1e7a6a9`

### 5b. Adicionar ao `config.yml` do cloudflared

Edite o arquivo de configuração do túnel (ex.: `/etc/cloudflared/config.yml`) e acrescente as duas entradas **antes** do catch-all final:

```yaml
  - hostname: solorpg.1nodado.com.br
    service: http://localhost:80
    originRequest:
      httpHostHeader: solorpg.1nodado.com.br

  - hostname: api.solorpg.1nodado.com.br
    service: http://localhost:80
    originRequest:
      httpHostHeader: api.solorpg.1nodado.com.br
```

Reiniciar o tunnel para aplicar:

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

---

## 6. Caddy (reverse proxy local)

O Caddyfile usa um único bloco `:80` com `auto_https off` e matchers nomeados por `host`. Acrescente os dois blocos abaixo **dentro** do bloco `:80 { }` existente, junto com os demais sites:

```caddyfile
    @solorpg host solorpg.1nodado.com.br
    handle @solorpg {
        reverse_proxy localhost:3000
    }

    @api-solorpg host api.solorpg.1nodado.com.br
    handle @api-solorpg {
        reverse_proxy localhost:8000 {
            transport http {
                response_header_timeout 5m
            }
        }
    }
```

> O timeout de 5 minutos na API é necessário porque chamadas ao LLM (DeepSeek) podem demorar.

Exemplo do Caddyfile completo após a adição (trecho relevante):

```caddyfile
{
    auto_https off
}

:80 {
    # ... outros sites existentes ...

    @solorpg host solorpg.1nodado.com.br
    handle @solorpg {
        reverse_proxy localhost:3000
    }

    @api-solorpg host api.solorpg.1nodado.com.br
    handle @api-solorpg {
        reverse_proxy localhost:8000 {
            transport http {
                response_header_timeout 5m
            }
        }
    }
}
```

Aplicar sem derrubar os outros sites:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile   # verifica sintaxe
sudo systemctl reload caddy
```

Testar a partir do próprio servidor (HTTP direto ao Caddy, sem tunnel):

```bash
curl -s -H "Host: api.solorpg.1nodado.com.br" http://localhost/health
# {"status":"ok","database_ok":true,...}

# Após tunnel configurado e DNS propagado, testar via HTTPS (Cloudflare):
curl -s https://api.solorpg.1nodado.com.br/health
```

> **Nota:** como `NEXT_PUBLIC_API_URL` é uma variável de **build-time** do Next.js, o `.env` deve ter `https://api.solorpg.1nodado.com.br` **antes** do `docker compose up --build`. Se precisar alterar depois:
>
> ```bash
> cd /opt/apps/solorpg/app
> docker compose up -d --build frontend
> ```

---

## 7. Interagir com o banco diretamente

O arquivo está no host, **acessível a qualquer momento** — sem precisar entrar no container:

```bash
# Listar tabelas
sqlite3 /opt/apps/solorpg/data/wfrp_solo.db ".tables"

# Query direta
sqlite3 /opt/apps/solorpg/data/wfrp_solo.db "SELECT * FROM users;"

# Modo interativo
sqlite3 /opt/apps/solorpg/data/wfrp_solo.db
```

Para inspecionar sem parar o backend (leitura é segura com SQLite WAL mode):

```bash
sqlite3 /opt/apps/solorpg/data/wfrp_solo.db "PRAGMA journal_mode;"
```

---

## 8. Backup do banco

```bash
# Backup com backend rodando (SQLite WAL — geralmente seguro)
cp /opt/apps/solorpg/data/wfrp_solo.db \
   "/opt/apps/solorpg/data/wfrp_solo.db.$(date +%Y%m%d_%H%M)"

# Backup garantido (para o backend primeiro)
docker compose -f /opt/apps/solorpg/app/docker-compose.yml stop backend
cp /opt/apps/solorpg/data/wfrp_solo.db \
   "/opt/apps/solorpg/data/wfrp_solo.db.$(date +%Y%m%d_%H%M)"
docker compose -f /opt/apps/solorpg/app/docker-compose.yml start backend
```

Cron diário (como root ou com sudo):

```bash
sudo crontab -e
# Adicione:
# 3 2 * * * cp /opt/apps/solorpg/data/wfrp_solo.db "/opt/apps/solorpg/data/wfrp_solo.db.$(date +\%Y\%m\%d)" 2>&1
```

---

## 9. Smoke test pós-deploy

```bash
# API saudável
curl -s https://api.solorpg.1nodado.com.br/health

# Frontend acessível
curl -Is https://solorpg.1nodado.com.br | head -5
```

1. Abra `https://solorpg.1nodado.com.br/login`
2. Entre com a senha definida em `ADMIN_PASSWORD`
3. Personagem pré-gerado deve aparecer em `/character`
4. `/register` deve redirecionar para `/login` (fase 1)

---

## 10. Atualizações

```bash
cd /opt/apps/solorpg/app
git pull
docker compose up -d --build
# O banco em /opt/apps/solorpg/data/ não é tocado
```

---

## 11. Troubleshooting

| Problema | Solução |
|----------|---------|
| Backend não sobe | `docker compose logs backend` — verificar `JWT_SECRET` e `ADMIN_PASSWORD` |
| `database_ok: false` | Permissões em `/opt/apps/solorpg/data`; verificar `ls -la` |
| CORS error no browser | `CORS_ORIGINS` deve ser exatamente `https://solorpg.1nodado.com.br` |
| Frontend chama API errada | Rebuild após mudar `NEXT_PUBLIC_API_URL`: `docker compose up -d --build frontend` |
| 502 Bad Gateway | Container não subiu; `docker compose ps` e `docker compose logs` |
| Caddy tenta HTTPS e falha | Confirmar prefixo `http://` no Caddyfile para esses domínios |
| Caddy: `address already in use` | Outra porta 80/443 ocupada; `sudo ss -tlnp \| grep ':80'` |
| Tunnel não roteia / 502 | `sudo systemctl status cloudflared`; verificar entradas no `config.yml` |
| Tunnel: host não reconhecido | Confirmar CNAME no painel Cloudflare com proxy ativo (laranja) |
| 403 em wizard de personagem | Esperado — `ENABLE_CUSTOM_CHARGEN=false` na fase 1 |
| Imagens não carregam | Configurar `CLOUDFLARE_*` ou aceitar placeholder |

### Dados 3D não aparecem (erros `colliderFaceMap` no console)

Os dados 3D usam **Ammo.js** (física em WebAssembly) + Workers do browser. Dois problemas comuns em produção:

#### 1. MIME type do arquivo `.wasm`

O arquivo `ammo.wasm.wasm` (física Ammo.js do DiceBox) deve ser servido com `Content-Type: application/wasm`. Adicione ao seu **Caddyfile**:

```caddyfile
@wasm {
    path *.wasm
}
header @wasm Content-Type "application/wasm"
```

Posicione esse bloco dentro da `handle` do domínio frontend:

```caddyfile
http://solorpg.1nodado.com.br {
    @wasm {
        path *.wasm
    }
    header @wasm Content-Type "application/wasm"

    reverse_proxy localhost:3000
}
```

Após editar: `sudo systemctl reload caddy`

Verifique com:
```bash
curl -I https://solorpg.1nodado.com.br/assets/dice-box/assets/ammo/ammo.wasm.wasm \
  | grep content-type
# Esperado: content-type: application/wasm
```

#### 2. Headers COOP/COEP

O Next.js já inclui esses headers via `next.config.js` desde a versão `0.3.2`. Se por algum motivo não estiverem chegando, adicione ao Caddyfile:

```caddyfile
http://solorpg.1nodado.com.br {
    header Cross-Origin-Opener-Policy "same-origin"
    header Cross-Origin-Embedder-Policy "require-corp"
    reverse_proxy localhost:3000
}
```

Verifique com:
```bash
curl -I https://solorpg.1nodado.com.br | grep -i "cross-origin"
# Esperado:
# cross-origin-opener-policy: same-origin
# cross-origin-embedder-policy: require-corp
```

#### 3. Assets ausentes no container

Se o build Docker falhar com `ERROR: ammo.wasm.wasm missing after prepare:dice`, verifique se `node_modules/@3d-dice/dice-box` existe na etapa `builder`. Isso indica que o `npm install` não instalou o pacote — confirme se `package.json` tem `"@3d-dice/dice-box": "^1.1.4"` e rebuilde do zero: `docker compose build --no-cache frontend`.

---

## 12. Desenvolvimento local com Docker

Na raiz do repo (sem Caddy):

```bash
cp .env.docker.example .env
# Edite: ADMIN_PASSWORD, DEEPSEEK_API_KEY (ou LLM_PROVIDER=mock)
# WFRP_DATA_DIR pode ficar como ./data

docker compose up --build
```

Acesse **http://127.0.0.1:3000** (frontend) e **http://127.0.0.1:8000/health** (API).
Banco fica em `./data/wfrp_solo.db` no workspace.

---

## Referências

- [Arquitetura](architecture.md)
- [Checklist de validação MVP](mvp-validation-checklist.md)
- [`docker-compose.yml`](../docker-compose.yml)
- [`.env.docker.example`](../.env.docker.example)
