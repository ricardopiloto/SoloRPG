# Frontend vs Backend — WFRP Solo

**Versão:** 1.0  
**Data:** 2026-06-11  
**Princípio:** Regras e estado são código; narrativa é LLM; memória é banco de dados.

Este documento detalha o que cada camada faz, o que **nunca** deve cruzar a fronteira, e onde está cada responsabilidade no repositório.

---

## Visão macro

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│  UI imersiva · input texto · animações · sidebars · i18n PT-BR  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP REST (+ SSE streaming)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                        │
│  Orquestração · regras WFRP4e · sinais LLM · memória · imagens  │
└───────┬─────────────────┬──────────────────────┬──────────────┘
        │                 │                      │
        ▼                 ▼                      ▼
   PostgreSQL/       DeepSeek API           Flux 1.1 Pro
   SQLite +          (GM narrativa)         (ilustrações)
   pgvector
```

---

## Backend — o que é e o que faz

**Stack:** Python 3, FastAPI, SQLAlchemy, asyncpg/aiosqlite, pgvector  
**Pasta:** `backend/app/`  
**Porta default:** `8000`

### Responsabilidades exclusivas do backend

| Responsabilidade | Por quê no backend |
|------------------|-------------------|
| Rolagem de dados (d100, d10) | Impossível manipular pelo jogador |
| Cálculo de testes, dano, wounds, críticos | Determinístico e auditável |
| Fate Points e Fortune Points | Estado autoritativo |
| XP, progressão, compra de avanços | Regras WFRP4e em código |
| Morte permanente | Transição de estado no banco |
| Parser de sinais LLM (`[TESTE]`, `[IMAGEM]`, etc.) | Contrato entre prompt e código |
| Montagem de contexto para DeepSeek | XML campanha/personagem/memória |
| Memória persistente (NPCs, eventos, karma) | Fora da context window |
| Busca semântica (pgvector ou fallback) | Dados de campanha longa |
| Geração de imagens Flux | API key server-side |
| Timer de sessão e modo COMBATE | Autoridade de estado |

### O backend **nunca** deve

- Delegar rolagem de dados ou cálculo de wounds à LLM  
- Expor API keys (DeepSeek, Flux) ao frontend  
- Confiar em valores de dados enviados pelo cliente  
- Quebrar personagem de GM (isso é responsabilidade do prompt + orchestrator)

### Estrutura de pastas (backend)

```
backend/app/
├── main.py              # FastAPI app, lifespan, CORS, /health
├── config.py            # Variáveis de ambiente
├── api/
│   └── routes.py        # Endpoints REST (/api/...)
├── db/
│   ├── models.py        # SQLAlchemy: personagem, campanha, sessão, NPCs...
│   └── database.py      # Engine async, session factory
├── rules/               # Motor WFRP4e (PURO Python, sem LLM)
│   ├── dice.py          # d100, d10
│   ├── tests.py         # Testes de atributo/perícia
│   ├── combat.py        # Ataque CC/distância, iniciativa
│   ├── criticals.py     # Critical hits
│   ├── fate.py          # Pontos de Destino
│   └── careers.py       # XP, avanços, custos
├── llm/
│   ├── adapter.py       # DeepSeek / mock / Anthropic
│   ├── prompts.py       # Carrega gm-system-prompt.md
│   └── signals.py       # Parse [TESTE], [IMAGEM], [FIM_SESSAO]...
├── services/
│   ├── gm_orchestrator.py   # Loop turno: LLM ↔ regras ↔ persistência
│   ├── session.py           # Sessão, timer, combate
│   ├── campaign.py          # Ciclo de vida campanha
│   ├── character.py         # Personagem, pregen, progressão
│   ├── memory.py            # 4 camadas de memória, context XML
│   └── images.py            # Fila Flux / placeholders
└── schemas/
    └── api.py           # Pydantic request/response
```

### APIs REST (backend expõe, frontend consome)

| Endpoint | Função |
|----------|--------|
| `GET /health` | Status do serviço e banco |
| `GET/POST /api/characters` | Listar, criar personagem |
| `POST /api/characters/pregen` | Personagem pré-gerado |
| `POST /api/characters/{id}/progression/skill` | Comprar perícia |
| `POST /api/characters/{id}/progression/talent` | Comprar talento |
| `GET/POST /api/campaigns` | Campanhas |
| `POST /api/campaigns/{id}/sessions` | Iniciar sessão |
| `POST /api/sessions/{id}/turn` | Enviar ação do jogador |
| `GET /api/campaigns/{id}/diary` | Diário |
| `GET /api/campaigns/{id}/map` | Regiões do mapa |

**Planejados (propostas OpenSpec):**

| Endpoint | Change |
|----------|--------|
| `POST /api/sessions/{id}/roll` | `add-player-test-agency` |
| SSE stream de turno | `configure-deepseek-llm` |
| `POST /campaigns/{id}/complete` | `add-campaign-flows` |
| `GET /campaigns/{id}/active-session` | `add-campaign-flows` |
| `GET /characters/{id}/progression` | `add-campaign-flows` |
| `GET /api/images/{job_id}/file` | `switch-to-cloudflare-workers-ai` |
| `GET /api/images/{job_id}` | `add-flux-visual-pipeline` |

### Integrações externas (backend)

| Serviço | Uso | Variáveis |
|---------|-----|-----------|
| **DeepSeek** | GM narrativo | `LLM_PROVIDER`, `DEEPSEEK_API_KEY`, `LLM_MODEL` |
| **PostgreSQL + pgvector** | Produção / memória semântica | `DATABASE_URL` |
| **SQLite** | Dev local rápido | `DATABASE_PROFILE=sqlite-dev` |
| **Cloudflare Workers AI** | Ilustrações (`flux-1-schnell`) | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` |

### Fluxo de um turno (backend)

```
1. Frontend POST /sessions/{id}/turn { action: "..." }
2. Orchestrator monta contexto XML + system prompt
3. DeepSeek responde (narração + sinais JSON)
4. Backend parseia sinais:
   [TESTE]     → rules engine → resultado (não narra ainda se add-player-test-agency)
   [IMAGEM]    → fila Flux
   [FIM_SESSAO]→ persiste resumo, XP, karma
   [NOVA_CAMPANHA] → cria metadados campanha
5. Resposta JSON → frontend (narrativa, rolls, images, session_ended)
```

---

## Frontend — o que é e o que faz

**Stack:** Next.js 14, React, TailwindCSS, TypeScript  
**Pasta:** `frontend/src/`  
**Porta default:** `3000`

### Responsabilidades exclusivas do frontend

| Responsabilidade | Por quê no frontend |
|------------------|---------------------|
| Layout imersivo (chat + sidebars) | Experiência do jogador |
| Input de texto livre | Único meio de ação (product-brief) |
| Animação visual do d100 | Feedback imersivo (resultado vem do backend) |
| Botão "Rolar dado" | Agência do jogador (dispara API backend) |
| Exibição ficha, wounds bar, Fate Points | Leitura de estado (GET character) |
| Timer / modo sessão visível | Reflete estado da sessão |
| Diários read-only | Apresentação de resumos |
| Mapa e inventário visual | Apresentação de assets |
| Streaming de texto GM | UX de latência |
| PT-BR / i18n | Strings de interface |

### O frontend **nunca** deve

- Rolar dados ou calcular sucesso/falha  
- Armazenar estado autoritativo de campanha (só cache de UI)  
- Chamar DeepSeek ou Flux diretamente  
- Mostrar karma/reputação como números  
- Permitir editar diário ou mapa (somente leitura)  
- Usar controles de videogame (click-to-move, botões de ação)

### Estrutura de pastas (frontend)

```
frontend/src/
├── app/
│   ├── layout.tsx       # Shell HTML, lang=pt-BR
│   ├── page.tsx         # App principal (home + sessão + recap)
│   └── globals.css      # Tema WFRP, tipografia
├── components/
│   ├── CharacterSheet.tsx    # Ficha na sidebar esquerda
│   ├── SidePanels.tsx        # Inventário, mapa, diário
│   └── DiceRollAnimation.tsx # Animação d100
└── lib/
    ├── api.ts           # Cliente HTTP → backend
    └── i18n.ts          # Strings PT-BR (i18n-ready)
messages/
└── pt-BR.json           # Traduções (a expandir)
```

### Telas (frontend)

| Tela | View state | Conteúdo |
|------|------------|----------|
| **Home** | `home` | Criar/selecionar personagem, campanhas, histórico |
| **Sessão ativa** | `session` | Chat + sidebars fixas |
| **Recap** | `recap` | Resumo sessão + XP |
| **Progressão** | `progression` | Gastar XP entre sessões |

### Layout da sessão (product-brief §5)

```
┌──────────────┬─────────────────────────┬──────────────┐
│   ESQUERDA   │        CENTRO           │   DIREITA    │
│              │                         │              │
│  Ficha       │  Narrativa GM (scroll)  │  Diário      │
│  Wounds bar  │  Ilustrações inline     │  campanha    │
│  Fate/Fortune│  Card de teste + roll    │  Diário      │
│  Perícias    │  Input discreto         │  personagem  │
│  Inventário  │                         │  Mapa        │
│  Modo+timer  │                         │              │
└──────────────┴─────────────────────────┴──────────────┘
```

---

## Divisão por feature do MVP

| Feature | Backend | Frontend |
|---------|---------|----------|
| GM narrativo | DeepSeek + orchestrator + prompt | Exibe texto (stream) |
| Testes d100 | Rola, calcula SL | Botão "Rolar dado", animação |
| Combate | Iniciativa, turnos, `[ESTADO_COMBATE]` | Contador turno, modo |
| Personagem | Schema, API, regras XP | Ficha, progressão UI |
| Campanha | Estado, NPCs, objetivos secretos | Histórico, continuar |
| Memória | PostgreSQL, pgvector, resumos | Diários read-only |
| Karma/reputação | Valores internos -100..100 | **Nunca exibir números** |
| Imagens Flux | Fila, cache, API | Inline no chat, mapa |
| Sessão timer | Calcula tempo restante | Header + sidebar |
| Fate Points | Deduz server-side | Sidebar esquerda |

---

## O que é compartilhado / documentação

| Item | Local | Quem usa |
|------|-------|----------|
| System prompt GM | `Docs/gm-system-prompt.md` | Backend injeta na DeepSeek |
| Product brief | `Docs/product-brief.md` | Referência ambos |
| Protocolo de sinais | `Docs/gm-system-prompt.md` | Backend parseia; LLM emite |
| Specs OpenSpec | `openspec/changes/` | Desenvolvimento |
| `.env.example` | Raiz | Backend + frontend |

---

## Infraestrutura (nem frontend nem backend app)

| Item | Pasta / arquivo | Função |
|------|-----------------|--------|
| Docker Compose | `docker-compose.yml` | PostgreSQL + pgvector local |
| Testes backend | `backend/tests/` | pytest |
| OpenSpec | `openspec/` | Specs e propostas |

---

## Regra de ouro

> **Se envolve número, dado, regra ou persistência → backend.**  
> **Se envolve pixels, texto na tela ou input do jogador → frontend.**

A LLM (DeepSeek) fica **sempre no backend**. O frontend só vê texto narrativo e metadados de UI (testes pendentes, URLs de imagem, timer).

---

## Protótipo Open Design → rotas Next.js

Referência visual: `open-design/.od/projects/a37408fc-73d7-4e3e-8d6f-2367528ff373/`. Gap completo em `Docs/prototype-gap-analysis.md`.

| Protótipo | Rota alvo | Responsabilidade frontend |
|-----------|-----------|---------------------------|
| `landing.html` | `/landing` | Marketing, CTA para campanha |
| `home.html` | `/` | Dashboard, campanha ativa, histórico |
| `character.html` | `/character` | Pregen + formulário custom |
| `campaigns.html` | `/campaigns` | Nova / continuar / histórico |
| `game.html` | `/play/[sessionId]` | Sessão ativa (core) |
| `session-end.html` | `/session/end` | Resumo + XP |
| `session-progression.html` | `/progression` | Gastar XP |
| `session-death.html` | `/session/death` | Morte do personagem |
| `dice-roll.html` | `DiceOverlay` | Componente, não rota |

OpenSpec: `add-frontend-prototype-parity`, `add-quick-roll-sidebar`.
