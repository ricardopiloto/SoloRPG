# Gap Analysis — Protótipo Open Design vs Frontend Atual

**Data:** 2026-06-13  
**Protótipo:** `open-design/.od/projects/a37408fc-73d7-4e3e-8d6f-2367528ff373/`  
**Código:** `frontend/src/` (8 arquivos, monolito em `page.tsx`)

---

## Resumo

| Área | Protótipo | Código atual | Gap |
|------|-----------|--------------|-----|
| Telas | 9 rotas distintas | 9 rotas App Router | **Resolvido** |
| Design system | `shared.css` completo | Tailwind + globals WFRP tokens | **Resolvido** |
| Sessão (game) | 3 colunas + resize | `/play/[sessionId]` 3 colunas + resize | **Resolvido** |
| Chat | Prosa contínua, sem bubbles | `ChatLog` narrative-block / player-line | **Resolvido** |
| Ficha | Wounds bar, gems, colapsáveis | `CharacterSidebar` | **Resolvido** |
| Diários | Tabs Campanha/Personagem | `DiarySidebar` | Parcial (só campanha no backend) |
| Teste GM | Card inline + 2 botões | `TestBlock` + roll API | **Resolvido** |
| Dado | Overlay CSS + Dice So Nice spec | `DiceOverlay` CSS cube | **Resolvido** |
| Quick roll | Sidebar clicável + popover | `QuickRollPopover` + API | **Resolvido** |
| Prepare overlay | Modal antes da sessão | `SessionPrepareOverlay` | **Resolvido** |
| Landing | Marketing page | `/landing` | **Resolvido** |
| Session end/death/progression | Telas dedicadas | Rotas dedicadas | **Resolvido** |
| Ilustrações inline | `scene-img` com polling Flux | `SceneImage` + `GET /api/images/{id}` | **Resolvido** |
| Mapa com imagem | `image_url` em regiões | `MapRegion.image_url` atualizado pelo pipeline | **Resolvido** |
| Inventário visual | Thumbnail em itens | `CharacterSidebar` com `image_url` em trappings | **Resolvido** |

---

## Tela a tela

### 1. Landing (`landing.html`)
- Hero split, proposta de valor, CTA
- **Atual:** ausente

### 2. Home (`home.html`)
- Welcome, campanha ativa, histórico com tags (ativa/concluída/morte)
- Empty state primeira visita
- **Atual:** lista simples personagens/campanhas

### 3. Character (`character.html`)
- Grid de pré-gerados + formulário custom
- **Atual:** só botões pregen

### 4. Campaigns (`campaigns.html`)
- Nova / continuar / histórico
- **Atual:** botão "Nova campanha" apenas

### 5. Game (`game.html`) — **core**
Protótipo inclui:
- `session-prepare` overlay
- Header: localização + número sessão
- Sidebar esquerda: identidade, wounds bar, fate gems ◆◇, colapsáveis, rollable attrs/skills/weapons, footer XP + modo/timer
- Chat: `narrative-block`, `player-line` (itálico direita), `scene-img`, `test-block`, `roll-system-msg`
- `dice-overlay` sobre chat (d100 cube)
- `quick-roll-popover` com mod ± e countdown 2s
- Input discreto + btn-send ícone
- Sidebar direita: tabs Campanha/Personagem
- Resize handles entre colunas
- **Atual:** layout fixo básico, bubbles, `DiceRollAnimation` inline, sem test card, sem quick roll

### 6. Session End (`session-end.html`)
- Resumo narrativo, XP, CTAs progressão/continuar
- **Atual:** view `recap` mínima

### 7. Progression (`session-progression.html`)
- Lista comprável de perícias/talentos/atributos
- **Atual:** um botão hardcoded "Atletismo +1"

### 8. Death (`session-death.html`)
- Narração final, campanha inacabada, nova campanha
- **Atual:** ausente

### 9. Dice Roll (`dice-roll.html`)
- Rolagem inline no chat-log via `DiceRoller.rollInChat()` (bloco `.chat-roll-entry`, stage 3D ~280px)
- **Atual:** `ChatRollEntry` inline em `ChatLog` — alinhado ao protótipo

---

## Design tokens (protótipo → Tailwind)

| Token protótipo | Valor | Tailwind alvo |
|-----------------|-------|---------------|
| `--bg` | `#0D0B08` | `wfrp-bg` |
| `--surface` | `#1A1612` | `wfrp-surface` |
| `--surface-raised` | `#241E17` | `wfrp-raised` |
| `--fg` | `#E8DCC8` | `wfrp-fg` |
| `--muted` | `#9E8E72` | `wfrp-muted` |
| `--accent` | `#C9973A` | `wfrp-accent` |
| `--danger` | `#8B1A1A` | `wfrp-danger` |
| `--success` | `#3A5C2E` | `wfrp-success` |
| `--combat` | `#1E2D4A` | `wfrp-combat` |

Fontes: Cinzel (títulos), Crimson Text (narrativa), Source Sans 3 (UI), JetBrains Mono (dados).

---

## Propostas OpenSpec geradas

| Change | Escopo |
|--------|--------|
| `add-frontend-prototype-parity` | Design system + 9 telas + sessão imersiva |
| `add-quick-roll-sidebar` | Quick roll sidebar + API |
| *(existentes)* `add-player-test-agency`, `configure-deepseek-llm`, etc. | Ver `development-order.md` |

**Nota:** `add-immersive-session-ui` é **substituída** por `add-frontend-prototype-parity` (escopo mais completo e ancorado no protótipo).
