# Documentação — WFRP Solo

Índice da pasta `Docs/`. Use este arquivo como ponto de entrada.

## Guias de implementação

| Documento | Conteúdo |
|-----------|----------|
| [development-order.md](development-order.md) | Ordem de fases, dependências, OpenSpec por etapa |
| [frontend-backend-split.md](frontend-backend-split.md) | O que é frontend vs backend, APIs, pastas |
| [prototype-gap-analysis.md](prototype-gap-analysis.md) | Gap protótipo Open Design ↔ código atual |
| [ux-spec.md](ux-spec.md) | Design visual + comportamental (grimório, chat, dado) |
| [session-flow.md](session-flow.md) | Fluxos Mermaid (campanha, turno, combate, fim) |
| [database-schema.md](database-schema.md) | Schema PostgreSQL + pgvector alvo |

## Produto e regras

| Documento | Conteúdo |
|-----------|----------|
| [product-brief.md](product-brief.md) | Visão, MVP, layout, fluxo de testes |
| [mvp-validation-checklist.md](mvp-validation-checklist.md) | Checklist manual campanha 3–5 sessões (DeepSeek) |
| [gm-system-prompt.md](gm-system-prompt.md) | Persona GM, sinais JSON, modos de sessão |
| [technical-research.md](technical-research.md) | Arquitetura, memória, stack |
| [brainstorming-session-2026-06-07-0212.md](brainstorming-session-2026-06-07-0212.md) | Sessão inicial de ideação |

## Decisões técnicas (implementação vs spec original)

| Tópico | Spec original | Implementação atual |
|--------|---------------|---------------------|
| LLM | Claude (product-brief v1.1) | **DeepSeek** (`deepseek-chat`) — ver `configure-deepseek-llm` |
| Backend | Node.js (technical-research v1.1) | **FastAPI/Python** (já implementado) |
| Imagens | Cloudflare Workers AI (FLUX.1 Schnell) | Cloudflare Workers AI |
| Protótipo UI | — | Open Design `a37408fc-73d7-4e3e-8d6f-2367528ff373` |

## Protótipo Open Design (referência visual)

**Caminho local:** `/home/ricardosobral/Documents/Desenvolvimento/open-design/.od/projects/a37408fc-73d7-4e3e-8d6f-2367528ff373/`

| Tela | Arquivo | Rota Next.js alvo |
|------|---------|-------------------|
| Launcher | `index.html` | `/` (dev) ou omitir em prod |
| Landing | `screens/landing.html` | `/landing` |
| Home | `screens/home.html` | `/` |
| Personagem | `screens/character.html` | `/character` |
| Campanhas | `screens/campaigns.html` | `/campaigns` |
| Sessão | `screens/game.html` | `/play/[sessionId]` |
| Fim de sessão | `screens/session-end.html` | `/session/end` |
| Progressão | `screens/session-progression.html` | `/progression` |
| Morte | `screens/session-death.html` | `/session/death` |
| Dado (ref.) | `screens/dice-roll.html` | componente overlay |

**CSS de referência:** `css/shared.css` (tokens), `css/game.css` (sessão), `css/dice.css`

## OpenSpec

Propostas ativas em `openspec/changes/`. Ver [development-order.md](development-order.md) para ordem de aplicação.
