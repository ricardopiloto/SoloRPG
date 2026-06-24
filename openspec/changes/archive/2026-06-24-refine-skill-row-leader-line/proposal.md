# Proposal: refine-skill-row-leader-line

**Data:** 2026-06-23  
**Status:** Draft (revisado)  
**Relacionado:** `show-skill-target-in-sidebar`, `refine-skill-row-target-display`  
**Arquivos afetados:** `CharacterSidebar.tsx`, `globals.css`, `messages/pt-BR.json` (cabeçalhos)

---

## Why

As linhas de perícia na sidebar exibem apenas nome e alvo numérico. O jogador não vê de relance **qual atributo** vincula a perícia nem **quantos avanços** possui — precisa inferir mentalmente a composição do alvo.

O pedido original pedia uma leader tracejada ligando nome ao número (`Arrombamento --------------------- 28`). A revisão mantém esse objetivo de clareza visual, mas expande para um **mini-layout tabular** com quatro colunas explícitas:

| Nome | Atributo | Avanços | Alvo |
|------|----------|---------|------|
| Arrombamento | Dex | 4 | 28 |

- **Atributo** — sigla do atributo vinculado (`Dex`, `S`, `BS`…), **não** o valor numérico do atributo
- **Avanços** — quantidade de avanços na perícia; exibir `0` quando não houver
- **Alvo** — valor total de rolagem (`computeSkillTarget` = atributo + avanços)

---

## What Changes

### Cabeçalho da tabela (uma vez por seção)

Acima da lista de perícias, dentro do `CollapsibleSection` de skills, uma linha de cabeçalho sutil (não clicável):

```
Nome          Atributo  Avanços  Alvo
```

Labels via i18n (`character.skillColName`, `character.skillColAttribute`, etc.) ou abreviações fixas se a sidebar for estreita.

### Linha de perícia (grid 4 colunas + leader)

Cada perícia continua sendo um `<button>` clicável para quick roll, com CSS grid:

| Coluna | Conteúdo | Notas |
|--------|----------|-------|
| Nome | `s.name` + leader tracejada | Leader preenche o espaço restante **dentro** da coluna nome, antes das colunas fixas |
| Atributo | `s.linked_attribute` | Sigla apenas — ex: `Dex`, não `28` |
| Avanços | `advances` | Sempre numérico, inclusive `0` |
| Alvo | `target` | Resultado de `computeSkillTarget` |

Estrutura prevista:

```tsx
<button className="skill-row grid ...">
  <span className="skill-row-name">
    <span className="truncate">{s.name}</span>
    <span className="skill-row-leader" aria-hidden />
  </span>
  <span className="skill-row-attr">{s.linked_attribute}</span>
  <span className="skill-row-adv">{advances}</span>
  <span className="skill-row-target">{target}</span>
</button>
```

Grid sugerido: `grid-cols-[minmax(0,1fr)_2.25rem_2.25rem_2.5rem] gap-x-2 items-baseline`

### CSS

- `.skill-row-header` — mesma grid das linhas; texto `text-[10px] uppercase text-wfrp-muted`
- `.skill-row-name` — `flex min-w-0 items-baseline`
- `.skill-row-leader` — `flex: 1`, `border-bottom: 1px dashed`, opacidade ~25%, `margin-left: 0.25rem`
- `.skill-row-attr`, `.skill-row-adv`, `.skill-row-target` — `font-mono tabular-nums text-[11px] text-wfrp-muted shrink-0 text-right`
- `.skill-row-target` — pode usar cor ligeiramente mais forte (`text-wfrp-fg`) para destacar o alvo

### Escopo

- **Somente** seção de perícias em `CharacterSidebar`
- Inventário e atributos **não** alterados

---

## Capabilities

### Modified Capabilities

- **quickroll-ux**: linhas de perícia exibem tabela Nome / Atributo / Avanços / Alvo com leader tracejada na coluna nome

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/components/character/CharacterSidebar.tsx` | Cabeçalho + grid 4 colunas por perícia |
| `frontend/src/app/globals.css` | Classes `.skill-row`, `.skill-row-header`, colunas e leader |
| `frontend/messages/pt-BR.json` | Labels opcionais das colunas |

---

## Non-Goals

- Mostrar o **valor** do atributo base na coluna Atributo (só a sigla)
- Tabela sortável ou filtros
- Leader line em inventário ou cards de atributo
- Alterar cálculo de `computeSkillTarget`

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| Grid 4 colunas com leader só na coluna Nome | Leader atravessando toda a linha até Alvo | Colunas fixas de Attr/Adv/Alvo precisam alinhar verticalmente entre linhas |
| Avanços sempre visíveis (`0`) | Omitir quando zero | Pedido explícito: "se for 0 mostre 0" |
| Cabeçalho textual | Sem cabeçalho | Tabela fica autoexplicativa; cabeçalho ajuda em sidebar estreita |
