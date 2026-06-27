# Documentação — WFRP Solo

Índice da pasta `Docs/`. Para setup rápido, comece pelo [README na raiz](../README.md).

---

## Essenciais

| Documento | Quando usar |
|-----------|-------------|
| [architecture.md](architecture.md) | Entender arquitetura, fluxos e separação frontend/backend |
| [product-brief.md](product-brief.md) | Visão de produto, escopo MVP, requisitos |
| [debian-server-install.md](debian-server-install.md) | Deploy em servidor Linux Debian/Ubuntu |

---

## Referência técnica

| Documento | Conteúdo |
|-----------|----------|
| [database-schema.md](database-schema.md) | Schema SQLite + embeddings JSON |
| [ux-spec.md](ux-spec.md) | Paleta, tipografia, layout das telas |
| [gm-system-prompt.md](gm-system-prompt.md) | Prompt do GM e protocolo de sinais |
| [audio-engine.md](audio-engine.md) | Trilha ambiente (menu + tensão), roteamento, mute e sinal `[MUSICA]` |
| [character-background-prompt.md](character-background-prompt.md) | Prompt LLM para background (wizard) |

---

## Qualidade

| Documento | Conteúdo |
|-----------|----------|
| [mvp-validation-checklist.md](mvp-validation-checklist.md) | Roteiro manual campanha 3–5 sessões (DeepSeek) |

---

## OpenSpec

Propostas e specs de features em `openspec/changes/`. Contexto do projeto em `openspec/project.md`.

---

## Documentos removidos (consolidados)

Os arquivos abaixo foram fundidos ou descartados em 2026-06-22:

| Removido | Destino |
|----------|---------|
| `technical-research.md` | `architecture.md` |
| `frontend-backend-split.md` | `architecture.md` |
| `session-flow.md` | `architecture.md` |
| `development-order.md` | `openspec/changes/` + README |
| `prototype-gap-analysis.md` | Obsoleto (protótipo já integrado) |
| `phase1-release-runbook.md` | `debian-server-install.md` + README |
| `export-propostas-recentes.md` | `CHANGELOG.md` |
| `brainstorming-session-*.md` | Histórico de ideação (não operacional) |
