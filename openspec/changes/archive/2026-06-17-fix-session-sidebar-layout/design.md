# Design: Layout fixo de painéis na sessão

## Context

Layout atual (`page.tsx`, view `session`):

```
main (min-h-screen flex-row)
├── aside esquerdo (overflow-y-auto)  ← rola com a página
├── section central (flex-col)
│   ├── header
│   ├── chat (overflow-y-auto)
│   └── form input
└── aside direito (overflow-y-auto)   ← rola com a página
```

O `min-h-screen` permite que o documento inteiro cresça além da viewport, arrastando os asides no scroll global.

## Goals / Non-Goals

**Goals:**
- Viewport da sessão = `100vh`, sem scroll no `body`
- Asides fixos nas laterais; scroll exclusivo no chat
- Input sempre visível na base da coluna central

**Non-Goals:**
- Redesign visual dos painéis
- Colapsar/expandir painéis (futuro)
- Alterar layout das telas home/recap/progressão

## Decisions

### 1. Container raiz com altura fixa

```tsx
<main className="h-screen overflow-hidden flex flex-row">
```

Impede scroll global da página durante sessão ativa.

### 2. Asides sticky/fixed por coluna

```tsx
<aside className="h-screen shrink-0 overflow-y-auto lg:w-64">
```

- `h-screen`: ocupa altura total da viewport
- `overflow-y-auto`: scroll interno apenas se ficha/inventário/mapa/diário forem longos
- Não rolam quando o chat rola

### 3. Coluna central em grid flex

```tsx
<section className="flex-1 flex flex-col h-screen min-w-0">
  <header className="shrink-0" />
  <div className="flex-1 overflow-y-auto min-h-0">{/* chat */}</div>
  <form className="shrink-0">{/* input */}</form>
</section>
```

`min-h-0` é necessário para flex children respeitarem overflow.

### 4. Mobile (< lg)

Em telas estreitas, manter regra: chat scrollável isolado. Painéis podem ficar acima/abaixo do chat em stack, cada um com altura máxima e scroll interno — ou colapsados em tabs (fora do escopo; MVP mantém stack vertical com chat scrollável).

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Conteúdo longo nos asides cortado | `overflow-y-auto` interno nos painéis |
| iOS Safari 100vh | Usar `h-dvh` (dynamic viewport) como fallback |
| Diário muito longo | Scroll interno no painel direito, não no body |

## Migration Plan

Alteração puramente frontend; deploy independente; sem migração de dados.

## Open Questions

- Nenhuma bloqueante.
