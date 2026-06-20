# Design: Frontend Prototype Parity

## Referências

| Fonte | Caminho |
|-------|---------|
| Protótipo OD | `/home/ricardosobral/Documents/Desenvolvimento/open-design/.od/projects/a37408fc-73d7-4e3e-8d6f-2367528ff373/` |
| UX spec | `Docs/ux-spec.md` v1.0 |
| Gap analysis | `Docs/prototype-gap-analysis.md` |
| Session flows | `Docs/session-flow.md` |

## Mapeamento tela → rota

```
index.html (launcher dev)     → omitir em prod ou /dev
landing.html                  → app/landing/page.tsx
home.html                     → app/page.tsx
character.html                → app/character/page.tsx
campaigns.html                → app/campaigns/page.tsx
game.html                     → app/play/[sessionId]/page.tsx
session-end.html              → app/session/end/page.tsx
session-progression.html      → app/progression/page.tsx
session-death.html            → app/session/death/page.tsx
dice-roll.html                → components/dice/DiceOverlay.tsx
```

## Estrutura de pastas alvo

```
frontend/src/
├── app/
│   ├── layout.tsx              # fonts + theme provider
│   ├── page.tsx                # home
│   ├── landing/page.tsx
│   ├── character/page.tsx
│   ├── campaigns/page.tsx
│   ├── play/[sessionId]/page.tsx
│   ├── session/end/page.tsx
│   ├── session/death/page.tsx
│   └── progression/page.tsx
├── components/
│   ├── layout/                 # AppShell, Sidebars, ResizeHandle
│   ├── session/                # ChatLog, TestBlock, PlayerLine, SceneImage
│   ├── character/              # WoundsBar, FateGems, CollapsibleSection
│   ├── diary/                  # DiaryTabs, DiaryEntry
│   ├── dice/                   # DiceOverlay, D100Cube
│   └── campaign/               # CampaignCard, HistoryList
├── styles/
│   └── wfrp-tokens.css         # port de shared.css
├── lib/
│   ├── api.ts                  # fetch helpers
│   └── i18n.ts                 # messages/pt-BR.json loader
└── messages/
    └── pt-BR.json
```

## Design tokens (Tailwind extend)

Portar de `css/shared.css`:

- Cores: `wfrp-bg` `#0D0B08`, `wfrp-surface` `#1A1612`, `wfrp-accent` `#C9973A`, etc.
- Fontes: `font-display` Cinzel, `font-narrative` Crimson Text, `font-ui` Source Sans 3
- Sombras e bordas: `--border-subtle`, `--shadow-raised`

Usar `next/font/google` para as três famílias.

## Sessão (game.html) — componentes críticos

1. **SessionPrepareOverlay** — modal com duração estimada, aviso não pausável, CTA iniciar
2. **ChatLog** — `narrative-block`, `player-line` (itálico, alinhado direita), sem bubbles
3. **TestBlock** — card inline com perícia/alvo, botões "Rolar dado" + alternativa (delega roll a `add-player-test-agency`)
4. **DiceOverlay** — overlay absoluto sobre chat, d100 cube CSS, SR-only para leitores de tela
5. **CharacterSidebar** — wounds bar, fate gems ◆◇, attrs rollable (quick roll em proposta separada)
6. **DiarySidebar** — tabs Campanha/Personagem, read-only
7. **ResizeHandle** — drag para redimensionar colunas (localStorage persist)

## Decisões

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Router | App Router (já em uso) | Convenção Next.js 14 |
| Estado sessão | React state + API polling/SSE | Sem WebSocket no MVP |
| Dice 3D | CSS cube MVP | Protótipo usa CSS; `@3d-dice/dice-box` fase posterior |
| Landing em prod | Opcional via env | Launcher OD é dev-only |
| Substituição | `add-immersive-session-ui` | Escopo estritamente menor |

## Relação com propostas existentes

- `fix-session-sidebar-layout` — mantido; sidebars fixas no scroll
- `add-player-test-agency` — TestBlock consome API de roll
- `add-combat-orchestration` — modo COMBATE na sidebar (cor `--combat`)
- `add-campaign-flows` — telas character/campaigns/progression compartilham rotas
- `add-flux-visual-pipeline` — `SceneImage` inline no chat
