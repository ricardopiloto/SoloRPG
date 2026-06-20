# Change: Paridade do frontend com protótipo Open Design

## Why

O frontend atual (`page.tsx` monolítico, 8 arquivos) cobre ~15% da UI definida em `Docs/ux-spec.md` e no protótipo Open Design (`a37408fc-73d7-4e3e-8d6f-2367528ff373`). Gap documentado em `Docs/prototype-gap-analysis.md`.

A proposta `add-immersive-session-ui` cobre apenas a tela de sessão; o protótipo define **9 telas**, design system completo, overlay de dado, quick roll e fluxos de fim/progressão/morte.

## What Changes

- Design system WFRP (tokens, fontes Cinzel/Crimson Text/Source Sans 3) portado de `shared.css`
- Rotas Next.js App Router para 9 telas do protótipo
- Tela de sessão (`/play/[sessionId]`) com layout 3 colunas, resize handles, chat imersivo, test-block, dice overlay
- Sidebars: wounds bar, fate gems, colapsáveis, diários com tabs
- Telas de campanha: landing, home, character, campaigns, session-end, progression, death
- Overlay `session-prepare` antes de iniciar sessão
- i18n PT-BR via `messages/pt-BR.json`
- Substitui escopo de `add-immersive-session-ui` (não aplicar ambas)

## Impact

- Affected specs: `web-interface`, `identity-layers`
- Affected code: reestruturação completa de `frontend/src/` — `app/`, `components/`, `styles/`, `lib/`
- Referências: `Docs/ux-spec.md`, `Docs/session-flow.md`, protótipo OD `screens/*.html`, `css/*.css`
- Dependências: Fase 2 (`add-player-test-agency`, `add-combat-orchestration`) para test-block e combate; `add-flux-visual-pipeline` para `scene-img`

## Out of Scope (proposta separada)

- Quick roll sidebar + API → `add-quick-roll-sidebar`
- Integração `@3d-dice/dice-box` (fase 2 do dice overlay; MVP usa CSS cube do protótipo)
