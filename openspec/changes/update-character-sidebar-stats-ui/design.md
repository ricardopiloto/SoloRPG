# Design: update-character-sidebar-stats-ui

## Decisões

### Catálogo de perícias — fonte única

**Decisão:** Criar `backend/app/rules/skills.py` com `SKILL_CATALOG: dict[str, str]` (nome → atributo vinculado).

**Motivo:** Hoje o mapeamento está duplicado/parcial entre `gm_orchestrator.SKILL_ATTRIBUTES` e `careers.PROGRESSION_SKILLS`. Unificar evita drift e permite que frontend e quick roll usem a mesma lista.

**Migração:** `gm_orchestrator` e `get_progression_options` importam de `rules/skills.py`. `PROGRESSION_SKILLS` permanece como subconjunto "comprável com XP".

### Expor catálogo ao frontend

**Decisão:** `GET /rules/skills` → `{ "skills": [{ "name": "Atletismo", "linked_attribute": "Ag" }, ...] }`

**Alternativa rejeitada:** Duplicar lista no frontend — risco de inconsistência com backend no cálculo de alvo.

**Alternativa rejeitada:** Embutir no payload de personagem — personagem não muda o catálogo; endpoint estático é cacheável.

### Atributos — tooltip nativo vs componente

**Decisão:** Usar atributo HTML `title` nos cards + `aria-label` para acessibilidade.

**Motivo:** MVP simples; não há biblioteca de tooltip no projeto. Se hover for insuficiente em mobile, follow-up pode adicionar tooltip customizado.

### Layout dos cards

**Decisão:** Grid fixo `grid-cols-5 grid-rows-2 gap-1` (2 linhas × 5 colunas = 10 cards). Cards compactos — altura mínima, padding reduzido (`p-1` ou `p-1.5`), para não estourar a sidebar.

Anatomia de cada card:

```
┌──────┐
│  WS  │  text-[10px] ou text-xs, text-wfrp-muted, font-display
│  3̲4   │  text-lg font-mono tabular-nums; dezena com underline
└──────┘
```

**Bônus WFRP (dezena sublinhada):** valor exibido com 2 dígitos zero-padded quando < 10 (ex.: `08`). O primeiro dígito (dezena) recebe `underline decoration-wfrp-accent/60 decoration-1 underline-offset-2` — sinaliza visualmente o bônus de característica (+N) sem exibir o número do bônus separadamente.

Implementação sugerida em `AttributeCards.tsx`:

```tsx
const tens = Math.floor(value / 10);
const ones = value % 10;
<span className="text-lg font-mono">
  <span className="underline decoration-wfrp-accent/60">{tens}</span>
  {ones}
</span>
```

Estilo do card: `border border-wfrp-border rounded-sm bg-wfrp-surface/40 min-w-0`, hover `border-wfrp-accent/50` quando rollable. Flex column, items-center, justify-center.

Constante compartilhada `ATTRIBUTE_ORDER` e `ATTRIBUTE_LABELS` em `frontend/src/lib/wfrp-attributes.ts` (somente labels/tooltips — ordem espelha backend `ATTRIBUTE_NAMES`).

**Não responsivo para menos colunas nesta change** — sidebar já tem largura mínima fixa; 5 colunas cabem na faixa típica (~200–280px). Se overflow ocorrer, reduzir `gap` e font-size antes de mudar o grid.

### Perícias — lista colapsável (padrão Inventário)

**Decisão:** Reutilizar `CollapsibleSection` com trigger `collapsible-trigger`, idêntico ao Inventário. **Não** usar `<select>`.

Fluxo:
1. Jogador expande/colapsa "Perícias" via trigger
2. Lista exibe todas as entradas do catálogo como botões `rollable`
3. Clique na linha abre `QuickRollPopover` imediatamente

Layout de cada linha (espelha inventário):

```tsx
<button className="rollable w-full flex justify-between text-xs py-0.5">
  <span>{skillName}</span>
  {advances > 0 && <span className="text-wfrp-muted">+{advances}</span>}
</button>
```

`defaultOpen={true}` para manter visibilidade na sessão.

Perícias sem avanços: nome apenas, sem sufixo — ainda clicáveis para quick roll com alvo = atributo vinculado.

### Quick roll — perícia não possuída

**Decisão:** Backend calcula `target = linked_attribute + 0 + modifier`.

Frontend deve usar o mesmo cálculo para preview no popover (via catálogo + `character.attributes` + avanços locais).

---

## Riscos

| Risco | Mitigação |
|---|---|
| Lista incompleta vs expectativa do jogador | Documentar no spec que catálogo = MVP unificado; expandir em change futura |
| Select nativo feio em mobile | Lista colapsável com botões — mesmo padrão do inventário |
| Tooltip `title` invisível em touch | `aria-label` nos botões; nome completo disponível para leitores de tela |
