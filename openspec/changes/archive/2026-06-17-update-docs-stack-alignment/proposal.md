# Change: Alinhamento da documentação com implementação

## Why

Vários documentos em `Docs/` divergem do código e das decisões tomadas durante o MVP:

| Documento | Divergência |
|-----------|-------------|
| `product-brief.md` | Diz Claude-only; implementação usa DeepSeek |
| `technical-research.md` | Diz Node.js backend; código é FastAPI/Python |
| `session-flow.md` | Cloudflare Workers AI; proposta Flux 1.1 Pro |
| `development-order.md` | Referencia `add-immersive-session-ui` sem protótipo OD |
| `README.md` | Falta índice de novos docs (ux-spec, session-flow, etc.) |

## What Changes

- Adicionar seção "Decisões de implementação" em product-brief e technical-research
- Atualizar `development-order.md` v1.1 com Fase 3 expandida (prototype parity + quick roll)
- Criar `Docs/README.md` e `Docs/prototype-gap-analysis.md` (feito)
- Atualizar `frontend-backend-split.md` com referência ao protótipo OD
- Marcar `add-immersive-session-ui` como superseded por `add-frontend-prototype-parity`

## Impact

- Affected docs only — sem código
- Não altera specs em `openspec/specs/` (ainda vazias)
