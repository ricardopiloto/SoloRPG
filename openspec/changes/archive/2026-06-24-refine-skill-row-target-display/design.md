# Design: refine-skill-row-target-display

## Formato da label

**Decisão:** Meta à direita como `{linkedAttr}` entre colchetes + avanços opcionais.

```ts
function formatSkillRowMeta(linkedAttribute: string, advances: number): string {
  const tag = `[${linkedAttribute}]`;
  return advances > 0 ? `${tag} +${advances}` : tag;
}
```

Exemplo completo na UI: `{skill.name}` + espaço + `<span className="skill-row-meta">{formatSkillRowMeta(...)}</span>`

**Alternativa rejeitada:** Inline no nome (`Atirar (Arco) [BS] +5` num único `<span>`) — pior para truncate de nomes longos; nome e meta separados mantêm alinhamento com inventário.

## Alvo vs. exibição

| Conceito | Onde aparece |
|---|---|
| Valor do atributo (33) | Não na linha — visível nos cards de atributo |
| Sigla vinculada `[BS]` | Linha da perícia |
| Avanços `+5` | Linha da perícia |
| Alvo total 38 | QuickRollPopover ao clicar |

## Estilo

- `.skill-row-meta`: `text-wfrp-muted font-mono text-[11px] shrink-0 tabular-nums`
- Colchetes fazem parte do texto literal `[BS]`, não badge separado (MVP simples)

## Dependência

Requer catálogo `GET /rules/skills` com `linked_attribute` — já entregue por `update-character-sidebar-stats-ui`.
