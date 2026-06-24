# Proposal: add-skill-name-truncation-tooltip

**Data:** 2026-06-23  
**Status:** Draft  
**Relacionado:** `refine-skill-row-leader-line`  
**Arquivos afetados:** `CharacterSidebar.tsx`, novo componente utilitário (opcional)

---

## Why

Com o layout tabular de perícias, nomes longos (ex: "Atirar (Armas de Fogo)", "Conhecimento (Reikland)") são truncados com `truncate` na coluna Nome. O jogador vê apenas o início do texto e não consegue ler o nome completo sem adivinhar.

Um tooltip com o nome integral — **somente quando o texto está de fato truncado** — resolve isso sem poluir a UI com tooltips desnecessários em nomes curtos como "Arrombamento".

---

## What Changes

### Componente `TruncatedText` (reutilizável, mínimo)

Novo componente em `frontend/src/components/ui/TruncatedText.tsx`:

- Renderiza um `<span className="truncate">` com `ref`
- Em `useLayoutEffect` (e via `ResizeObserver` no elemento), compara `scrollWidth > clientWidth`
- Se truncado → define `title={children}` (tooltip nativo do browser)
- Se não truncado → `title` omitido (undefined)

Sem biblioteca de tooltip — segue o padrão já usado em `AttributeCards.tsx` (`title` nativo).

### Uso em `CharacterSidebar.tsx`

Substituir:

```tsx
<span className="truncate">{s.name}</span>
```

Por:

```tsx
<TruncatedText>{s.name}</TruncatedText>
```

Dentro de `.skill-row-name`, mantendo leader line e grid inalterados.

### Detecção de truncamento

| Evento | Reavalia truncamento |
|--------|----------------------|
| Mount inicial | Sim |
| Resize da sidebar (ResizeHandle) | Sim — via `ResizeObserver` no span |
| Mudança de `children` (nome da perícia) | Sim |

---

## Capabilities

### Modified Capabilities

- **quickroll-ux**: nomes de perícia truncados exibem tooltip com nome completo ao hover

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/components/ui/TruncatedText.tsx` | Novo — detecção de overflow + `title` condicional |
| `frontend/src/components/character/CharacterSidebar.tsx` | Usar `TruncatedText` na coluna Nome |

---

## Non-Goals

- Tooltip customizado estilizado (CSS popover) — `title` nativo é suficiente no MVP
- Tooltip em inventário ou outros truncates do app
- Tooltip em mobile long-press — comportamento nativo do OS para `title` é aceitável
- Tooltip nas colunas Atributo/Avanços/Alvo (não truncam)

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| `title` nativo condicional | Radix/shadcn Tooltip | Zero dependência; consistente com `AttributeCards` |
| Só quando truncado | `title` sempre | Evita tooltip redundante em nomes curtos |
| `ResizeObserver` | Só no mount | Sidebar é redimensionável — truncamento muda com largura |
