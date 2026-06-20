# Proposal: fix-chat-scroll-containment

**Data:** 2026-06-14  
**Status:** Draft  
**Escopo:** `frontend/` — `ChatLog.tsx` + `globals.css`

---

## Problema

Na tela de sessão (`/play/[sessionId]`), quando uma nova mensagem chega, **a página inteira sobe** em vez de apenas a área de conversa (`.chat-log`) rolar internamente.

### Causa raiz

`ChatLog.tsx` usa `scrollIntoView()` para rolar até o final da lista:

```ts
bottomRef.current.scrollIntoView({ behavior: "smooth" });
```

`scrollIntoView` sobe pela árvore DOM até encontrar o **primeiro ancestral com overflow de scroll ativo**. O container pretendido é `.chat-log` (que tem `overflow-y: auto`), mas `.chat-log` só é scrollável quando tem altura estritamente limitada pela cadeia `h-dvh → flex-1 min-h-0 → flex-1 min-h-0`.

O `<body>` em `layout.tsx` tem apenas `min-h-dvh` — o que dá `min-height: 100dvh` mas **não** impede scroll. Qualquer componente que "estoure" a cadeia flex (ex.: `SessionPrepareOverlay`, um `<DiceOverlay>` posicionado de forma incorreta, ou até diferença de renderização do Next.js) faz o `.chat-log` crescer ilimitadamente, tornando-o não-scrollável. O `scrollIntoView` então sobe para o `<body>` e rola a janela inteira.

### Evidências no código

| Arquivo | Linha | Problema |
|---------|-------|---------|
| `frontend/src/app/layout.tsx` | 32 | `<body className="font-ui min-h-dvh">` — sem `overflow-hidden` |
| `frontend/src/components/session/ChatLog.tsx` | 53–64 | `scrollIntoView` sem referência explícita ao container |

### Evidências de DOM ao vivo (inspeção em produção)

Posições capturadas pelo usuário via DevTools durante a sessão ativa:

| Elemento | top (viewport) | Interpretação |
|----------|----------------|---------------|
| `div.chat-log` | **−549px** | Elemento começa 549px **acima** do topo da janela — confirma `document.scrollTop ≈ 549` |
| `div.chat-input-area` | 95px | Aparece próxima ao topo, quando deveria estar fixada no rodapé |

Um `top` negativo em `getBoundingClientRect()` significa que o documento inteiro rolou 549px — o `<body>` está sendo scrollado, não o `.chat-log`.

### Restrição adicional: `chat-input-area` não pode participar do auto-scroll

`div.chat-input-area` é um **irmão direto** de `.chat-log` dentro de `.chat-column` (não está dentro do `.chat-log`). Com o fix de `scrollTop` explícito no `.chat-log`, o `chat-input-area` já ficará naturalmente fora do escopo do scroll. Esta restrição é satisfeita automaticamente pela solução.

Estrutura DOM correta:
```
section.chat-column
├── DiceOverlay (absolute inset-0)     ← fora do scroll
├── div.chat-log (overflow-y-auto)     ← ÚNICO elemento que scrolla
│   └── ... mensagens, anchor do dado
└── div.chat-input-area (shrink-0)     ← fixo no rodapé, FORA do scroll
```

---

## Solução proposta

### Fix 1 — Contenção de overflow no `<body>` (defesa em profundidade)

Adicionar `overflow-hidden` ao `<body>` em `globals.css` via a classe `body`. Na tela de sessão, o `<body>` nunca deve scrollar — todo scroll acontece dentro de `.chat-log` e das sidebars.

> Atenção: outras telas (landing, character, campaigns) usam layout padrão e podem precisar de scroll. O body da tela de sessão está encapsulado em `.game-shell { h-dvh overflow-hidden }`, que já bloqueia o body. O problema é que esse bloqueio não está sendo aplicado ao `<body>` em si quando o layout quebra.
>
> A alternativa mais segura é **não** bloquear o body globalmente, mas garantir que `.game-shell` force contenção completa — ver Fix 2.

### Fix 2 — Scroll explícito no container `.chat-log` (fix correto)

Substituir `scrollIntoView` por manipulação direta de `scrollTop` no container `.chat-log`, usando um segundo `ref` no componente `ChatLog`:

```ts
// Ref no container scrollável
const containerRef = useRef<HTMLDivElement>(null);

// No useEffect, em vez de scrollIntoView no sentinel:
if (containerRef.current) {
  containerRef.current.scrollTop = containerRef.current.scrollHeight;
}
```

Para o caso de scroll suave:
```ts
containerRef.current.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" });
```

Para scroll até um dado inline (`dice-roll`):
```ts
const el = diceRollRefs.current.get(newDiceRoll);
if (el && containerRef.current) {
  const offsetTop = el.offsetTop - containerRef.current.offsetTop;
  containerRef.current.scrollTo({ top: offsetTop - containerRef.current.clientHeight / 2, behavior: "smooth" });
}
```

Esta abordagem é **imune** a variações na cadeia flex: independentemente do layout, `scrollTop` no container correto sempre funciona.

### Fix 3 — Garantir `overflow: hidden` na `.game-shell` via `html` e `body`

Como `html` e `body` não têm `overflow: hidden`, se o `.game-shell` tiver altura estouro, o browser habilita scroll no documento. Adicionar ao `globals.css`:

```css
html, body {
  height: 100%;
  overflow: hidden;
}
```

Mas isso quebra outras páginas. A solução correta é uma **classe utilitária** aplicada apenas quando `.game-shell` está ativo — ou deixar que o Fix 2 resolva sem precisar tocar no body.

---

## Decisão de escopo

**Implementar Fix 2 como fix principal** (scroll explícito no container). Fix 1/3 como reforço dentro do `.game-shell` apenas, sem tocar no `body` global.

---

---

## Análise de impacto: rolagem de dados 3D (`DiceOverlay`)

### Por que o DiceOverlay não é afetado pelo fix

`DiceOverlay` renderiza três elementos com `absolute inset-0`:
- `#wfrp-dice-stage` (canvas WebGL do dado)
- backdrop escuro (`rgba(10, 8, 6, 0.88)`)
- UI de label/resultado

Todos usam `position: absolute` relativo a **`.chat-column`** (que tem `position: relative`) — eles são **irmãos** do `.chat-log`, não filhos. O `scrollTop` do `.chat-log` move o conteúdo do chat (narrativa, mensagens) mas **não** move os elementos `absolute` da `.chat-column`. O canvas do dado está fora da área scrollável por design.

```
.chat-column (position: relative)
├── #wfrp-dice-stage (absolute inset-0) ← não scrollado
├── .backdrop    (absolute inset-0) ← não scrollado
├── .result-ui   (absolute inset-0) ← não scrollado
├── .chat-log (overflow-y-auto)    ← scrollado pelo fix
│   ├── <MarkdownNarrative> ...
│   ├── <div role="anchor" data-dice-roll-id="...">  ← ancora vazia
│   └── <div ref={bottomRef}>
└── .chat-input-area (shrink-0)
```

### Risco na fórmula de scroll para o anchor do dado

A proposta original usa:
```ts
el.offsetTop - containerRef.current.offsetTop
```
Isso falha se houver elementos intermediários com `position` entre o anchor e o `.chat-log`. A fórmula correta usa `getBoundingClientRect`, que é relativo ao viewport e independe da hierarquia de `offsetParent`:

```ts
const containerRect = containerRef.current.getBoundingClientRect();
const elRect = el.getBoundingClientRect();
const scrollTarget =
  containerRef.current.scrollTop +
  (elRect.top - containerRect.top) -
  containerRef.current.clientHeight / 2 +
  el.clientHeight / 2;
containerRef.current.scrollTo({ top: scrollTarget, behavior: "smooth" });
```

> Nota: o anchor do dado é um `<div>` vazio (`height: 0`) — centralizar um elemento de altura 0 resulta em scroll para a posição onde ele aparece na lista, o que é aceitável pois o DiceOverlay cobre tudo com `absolute inset-0` durante a rolagem.

### Conclusão

A mudança de `scrollIntoView` → `scrollTop/scrollTo` no `.chat-log` **não afeta** a renderização ou posicionamento do DiceOverlay. O fix é seguro para a rolagem de dados.

---

## Sem breaking changes

- Não altera APIs
- Não altera comportamento de outras telas
- Visual do DiceOverlay é idêntico (absolute, fora do fluxo do chat-log)
- O visual da tela de sessão é idêntico — só o destino do scroll muda
