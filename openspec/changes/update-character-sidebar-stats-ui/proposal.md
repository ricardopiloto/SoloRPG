# Proposal: update-character-sidebar-stats-ui

**Data:** 2026-06-20  
**Status:** Draft  
**Escopo:** `frontend/src/components/character/` · `frontend/src/app/globals.css` · `backend/app/rules/` · `backend/app/services/gm_orchestrator.py`

---

## Problema

A sidebar de personagem na sessão exibe atributos como uma grade simples (sigla + valor em duas colunas) e lista apenas as perícias que o personagem **já possui** na seção colapsável. Isso diverge do pedido de UX e do `Docs/ux-spec.md` §6.2, que prevê quick roll para **todas** as perícias do jogo — não só as adquiridas.

**Estado atual:**

| Área | Comportamento |
|---|---|
| Atributos | Grid 2 colunas com sigla e valor; sem tooltip; sem cards |
| Perícias | Lista scrollável só com `character.skills`; perícias não possuídas ficam invisíveis |
| Quick roll (perícia) | Backend rejeita perícia ausente na ficha (`ValueError: Perícia não encontrada`) |
| Cálculo de alvo (frontend) | Usa `character.attributes.Ag` fixo para todas as perícias — bug |

---

## Solução proposta

### 1. Atributos em cards compactos com bônus visual

Substituir a grade de atributos por um grid fixo de **2 linhas × 5 colunas** (10 cards) — compacto o suficiente para caber na sidebar sem quebrar o layout.

Cada card segue esta hierarquia visual:

```
┌──────┐
│  WS  │  ← sigla, menor, parte superior
│  3̲4   │  ← valor grande no centro; dezena sublinhada = bônus WFRP
└──────┘
```

- **Sigla** no topo, fonte menor: WS, BS, S, T, I, Ag, Dex, Int, WP, Fel
- **Valor** centralizado, fonte maior (ex.: `text-lg font-mono`)
- **Dezena sublinhada:** o primeiro dígito do valor (bônus de característica WFRP) recebe sublinhado leve; ex. `34` → `<span underline>3</span>4`
- **Tooltip** (`title` nativo) com o nome completo em inglês:

| Sigla | Tooltip |
|---|---|
| WS | Weapon Skill |
| BS | Ballistic Skill |
| S | Strength |
| T | Toughness |
| I | Initiative |
| Ag | Agility |
| Dex | Dexterity |
| Int | Intelligence |
| WP | Willpower |
| Fel | Fellowship |

Cards permanecem **clicáveis** para quick roll (classe `rollable`), com hover conforme ux-spec.

**Restrição de tamanho:** cards devem ser visíveis e legíveis, mas não ocupar altura/largura excessiva — padding mínimo, sem labels extras dentro do card. O grid 5×2 é o layout inicial a validar visualmente.

Ordem fixa das siglas (não depende da ordem do objeto `attributes`).

### 2. Perícias em lista colapsável (mesmo padrão do Inventário)

Manter o componente **`CollapsibleSection`** já usado em Inventário (`button.collapsible-trigger` com título + `−`/`+`), em vez de dropdown `<select>`.

A seção **Perícias** SHALL:

- Usar `CollapsibleSection` com título "Perícias" (aberta por padrão, como antes)
- Listar **todas** as perícias do catálogo WFRP do MVP, ordenadas alfabeticamente
- Cada linha é um botão `rollable` clicável — mesmo padrão visual das entradas de inventário
- Exibir avanços à direita quando possuídas: `+2` (perícias sem avanço mostram só o nome)
- Clique abre o `QuickRollPopover` com alvo = `atributo_vinculado + avanços` (0 se não possuída)

```
Perícias                    −
  Atletismo              +2
  Arrombamento
  Escalar                  +1
  ...
```

### 3. Catálogo canônico de perícias (backend + frontend)

Centralizar o mapeamento `perícia → atributo_vinculado` em `backend/app/rules/skills.py`, unificando:

- `SKILL_ATTRIBUTES` (gm_orchestrator)
- `PROGRESSION_SKILLS` (careers)

Expor via endpoint leve `GET /rules/skills` (ou incluir no payload de sessão/personagem) para que o frontend não duplique a lista.

### 4. Backend: quick roll para perícias não possuídas

Em `execute_quick_roll`, quando `roll_type == "skill"`:

- Se a perícia existir no catálogo mas **não** na ficha → usar `advances = 0` e atributo vinculado do catálogo
- Se a perícia não existir no catálogo → `ValueError` (perícia inválida)

Isso alinha backend ao ux-spec §6.2 ("Perícias — todas").

---

## Não-escopo

- Redesenhar a página `/character` de criação (pode reutilizar cards depois, mas não é obrigatório nesta change)
- Catálogo completo WFRP4e (dezenas de perícias especializadas) — apenas as do MVP unificadas
- Tooltips traduzidos para PT-BR (nomes em inglês conforme pedido do usuário)
- Alterar inventário/armas ou popover de quick roll além do necessário para integrar a lista colapsável de perícias
- Dropdown `<select>` para perícias — rejeitado em favor de `CollapsibleSection`

---

## Impacto

- **Frontend:** novo componente `AttributeCards`, refatoração de `CharacterSidebar`, CSS para cards, i18n mínimo
- **Backend:** novo módulo `rules/skills.py`, endpoint de catálogo, relaxamento de validação em quick roll, testes
- **Specs:** delta em `web-interface` (capability arquivada — reintroduzida via change delta)
