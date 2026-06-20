# Tasks: add-frontend-prototype-parity

## 1. Design system

- [x] 1.1 Criar `styles/wfrp-tokens.css` portando tokens de `shared.css`
- [x] 1.2 Configurar `tailwind.config.ts` com cores/fontes WFRP
- [x] 1.3 Carregar Cinzel, Crimson Text, Source Sans 3 via `next/font`
- [x] 1.4 Criar `messages/pt-BR.json` com strings da ux-spec

## 2. Layout e navegação

- [x] 2.1 Criar `AppShell` com nav consistente (home, personagem, campanhas)
- [x] 2.2 Implementar `app/landing/page.tsx` (hero, CTAs)
- [x] 2.3 Refatorar `app/page.tsx` como home dashboard (campanha ativa, histórico)
- [x] 2.4 Implementar `app/character/page.tsx` (pregen grid + custom form)
- [x] 2.5 Implementar `app/campaigns/page.tsx` (nova, continuar, histórico)

## 3. Tela de sessão

- [x] 3.1 Criar `app/play/[sessionId]/page.tsx` com grid 3 colunas
- [x] 3.2 Implementar `ResizeHandle` com persistência localStorage
- [x] 3.3 Implementar `SessionPrepareOverlay` antes do primeiro turno
- [x] 3.4 Implementar `ChatLog` imersivo (narrative-block, player-line)
- [x] 3.5 Implementar `TestBlock` (aguarda `add-player-test-agency` API)
- [x] 3.6 Implementar `DiceOverlay` com d100 cube CSS
- [x] 3.7 Implementar `CharacterSidebar` (wounds bar, fate gems, colapsáveis)
- [x] 3.8 Implementar `DiarySidebar` com tabs Campanha/Personagem
- [x] 3.9 Input discreto + botão send ícone (sem bubble no input)

## 4. Telas pós-sessão

- [x] 4.1 Implementar `app/session/end/page.tsx` (resumo, XP, CTAs)
- [x] 4.2 Implementar `app/progression/page.tsx` (lista de avanços)
- [x] 4.3 Implementar `app/session/death/page.tsx` (morte, nova campanha)

## 5. Integração API

- [x] 5.1 Conectar home/campaigns às rotas existentes do backend
- [x] 5.2 Conectar sessão a SSE/streaming (`configure-deepseek-llm`)
- [x] 5.3 Conectar diários a endpoints de memória quando disponíveis

## 6. Validação

- [x] 6.1 Comparar visualmente cada rota com protótipo OD correspondente
- [x] 6.2 Verificar acessibilidade: aria-live no chat e dice overlay
- [x] 6.3 Testar resize sidebars e scroll fixo (`fix-session-sidebar-layout`)
- [x] 6.4 Atualizar `Docs/prototype-gap-analysis.md` marcando itens resolvidos
