# Tasks: Melhorias de UX no chat de jogo

## 1. Markdown no chat narrativo

- [x] 1.1 Instalar `react-markdown` em `frontend/`
- [x] 1.2 Criar componente `MarkdownNarrative` que renderiza Markdown com estilos `narrative-block` (negrito, itálico, listas, `---`)
- [x] 1.3 Substituir renderização do bloco narrativo em `ChatLog.tsx` pelo `MarkdownNarrative`
- [x] 1.4 Garantir que `player-line` e `roll-system-msg` permanecem como texto puro
- [x] 1.5 Validar que tokens em streaming são acumulados corretamente antes de renderizar Markdown (evitar flash de `**`) — streaming usa mesmo acumulador, cursor piscante indicando inProgresss

## 2. Auto-scroll para nova mensagem

- [x] 2.1 Adicionar `ref` no elemento sentinela (`<div>`) ao final do `.chat-log`
- [x] 2.2 `useEffect` em `ChatLog` que chama `scrollIntoView({ behavior: "smooth" })` toda vez que `entries` muda
- [x] 2.3 Durante streaming, scroll suave a cada novo token (entradas de streaming atualizam `entries`, triggering effect)
- [x] 2.4 Scroll inicial instantâneo (via `isFirstRender` ref), subsequentes suaves

## 3. Histórico de rolagens na sidebar

- [x] 3.1 Definir tipo `RollHistoryEntry` em `api.ts` (campo: `label`, `roll`, `target`, `success`, `levels`, `timestamp`)
- [x] 3.2 Em `useSessionPlay.ts`, acumular rolls recebidos via `TurnResponse.roll_results` e `quickRoll` em estado local `rollHistory`
- [x] 3.3 Passar `rollHistory` para `DiarySidebar` via page e atualizar assinatura de props
- [x] 3.4 Adicionar aba "Rolagens" em `DiarySidebar.tsx` com lista ordenada das entradas
- [x] 3.5 Estilizar cada entrada: label da perícia/atributo, número rolado em destaque, alvo, badge verde/vermelho, níveis de sucesso
- [x] 3.6 Aba Rolagens é a ativa por padrão (inicial `useState("rolls")`)

## 4. Testes e validação

- [x] 4.1 Build do frontend sem erros de TypeScript (`npm run build` ✓)
- [ ] 4.2 Verificar Playwright E2E: após rolar dado, a aba Rolagens deve ter entrada com resultado
- [ ] 4.3 Verificar que texto Markdown do GM (`**Você sente**`) renderiza como negrito visível
