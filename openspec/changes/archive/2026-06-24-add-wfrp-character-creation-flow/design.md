# Design: add-wfrp-character-creation-flow

## Context

**Estado atual**

- `POST /api/characters` aceita `CharacterCreate` livre — sem validação WFRP.
- `frontend/src/app/character/page.tsx` — inputs manuais de atributos, ferimentos e Destino.
- `backend/app/rules/skills.py` — catálogo parcial (~18 perícias) usado em progressão/quick-roll.
- `backend/app/rules/careers.py` — custos de progressão pós-sessão; sem dados de carreira Tier 1.
- `PlayerCharacter` — sem campos `species`, `resilience`, `movement`; suficiente para MVP com JSON em `attributes` + listas.

**Referência Foundry** (`src/apps/chargen/char-gen.js`)

Etapas e dependências:

```
species → career → attributes ─┐
         └→ skills-talents ────┤ (career required)
         └→ trappings ──────────┘
species → details
```

Ordem de implementação recomendada: dados (catálogos) → motor de regras → API → UI.

---

## Goals / Non-Goals

**Goals**

- Fluxo completo de criação WFRP4e para Humano, jogável sem GM.
- Toda mecânica de criação no backend; frontend só coleta escolhas e exibe rolagens.
- Personagem persistido é indistinguível de um pré-gerado válido para sessão/progressão.
- Pré-gerados continuam como atalho.

**Non-Goals**

- Multiespécie, Resiliência, movimento, marcas.
- Sincronizar com compendiums Foundry (apenas espelhar algoritmos).
- LLM na criação **mecânica** (atributos, perícias, validação) — apenas texto de background na etapa Detalhes.
---

## Decisions

### 1. Validação server-side obrigatória

**Decisão:** `POST /characters` só aceita `CharacterCreationSubmit` — payload estruturado do wizard já validado. Tentativa de envio livre retorna `422` com erros por etapa.

**Motivo:** Regra de ouro do projeto — mecânica nunca no LLM nem confiada ao cliente.

**Alternativa rejeitada:** Validar só no frontend — bypass trivial.

### 2. Rascunho stateless no cliente

**Decisão:** Estado do wizard em React (`useCharacterCreation`); `POST /characters/validate-creation` recebe rascunho parcial + `step` e devolve `{ valid, errors, computed }`.

**Motivo:** Sem auth/usuário; evita tabela `creation_drafts`. Opcional: `localStorage` como Foundry (`wfrp4e-chargen`).

### 3. Espécie MVP: Humano (Reikland)

**Decisão:** Única espécie jogável; config espelha Foundry `speciesCharacteristics.human` = `2d10+20` por atributo.

Constantes Humano (Core):

| Campo | Valor |
|-------|--------|
| Bônus característica | +20 (via fórmula `2d10+20`) |
| Movimento | 4 (informativo; não persistido no MVP) |
| Fate base | 0 |
| Resilience base | 0 |
| Extra (Destino/Resiliência) | pool a alocar (ex.: 2 pontos — validar contra livro; Foundry usa `speciesExtra`) |
| XP por rolar espécie | 20 |

**Follow-up:** `add-species-character-creation` adiciona Anão, Alto Elfo, etc.

### 4. Atributos — dois métodos, uma etapa

**Decisão:** Suportar **rolagem** e **compra com pontos** (mutuamente exclusivos por personagem), como no livro.

**Rolagem (Foundry `AttributesStage`):**

1. Rolar 10× `2d10+20` (Humano)
2. Opcional: trocar dois valores (drag ou select)
3. Opcional: um rerrolar completo
4. XP bônus: 50 (primeira rolagem), 25 (se trocou sem rerrolar), 0 (após rerrolar)

**Compra com pontos:**

- Pool 100; cada atributo 4–18 antes do bônus de espécie (Humano: valores finais = alocado + 20)
- XP bônus: 0

**Avanços na criação:**

- Máx. 5 avanços totais entre atributos (+10 cada no pool de XP de criação)
- Custo: 10 XP por avanço (desconta do `xp_total` disponível na criação)

**Destino:**

- `fate_max = species_fate_base + fate_allotted`
- `fate_allotted + resilience_allotted ≤ species_extra` — no MVP só persistimos Destino; validação de alocação usa `resilience_allotted` como contador fantasma se necessário para respeitar o pool, ou simplificamos: todo `extra` vai para Destino (Humano: 2 Fate) **se** o livro permitir sem Resiliência.

**Simplificação MVP documentada:** como Resiliência não é usada no motor, o pool `extra` da espécie é alocado **inteiro em Destino** (máx. 2 para Humano). Evita UI de Resiliência sem efeito mecânico.

### 5. Carreira — catálogo estático Core

**Decisão:** Arquivo `careers_catalog.json` (ou Python) com entradas Tier 1:

```python
{
  "id": "soldado",
  "name": "Soldado",
  "class": "warrior",  # martial / academic / ranger / rogue
  "career_group": "Soldado",
  "skills": ["Luta", "Atletismo", ...],  # lista para alocação
  "talents": ["Resolução", "Robusto"],   # escolher 1
  "trappings": [{"name": "...", "encumbrance": 1}, ...],
  "roll_weight": 1  # para tabela d100 Humano
}
```

**Rolagem de carreira:** tabela d100 Reikland (Core); implementar `roll_career_table()` determinístico com seed opcional para testes.

**XP bônus:** 50 (1ª rolagem), 25 (2ª leva de 2 carreiras), 0 (escolha manual ou rolagens extras).

### 6. Perícias e talentos

**Perícias de espécie (Humano):** lista fixa do Core; jogador distribui marcadores +0 / +3 / +5 com limites Foundry:

- máx. 3 perícias em +3
- máx. 3 perícias em +5

**Perícias de carreira:** 40 pontos entre as perícias listadas na carreira; máx. 10 por perícia; mín. 0.

**Talentos:**

- Espécie: tabelas aleatórias + escolhas (ex.: talentos aleatórios do Humano) — implementar subset Core
- Carreira: exatamente 1 dos talentos listados

**Perícias básicas:** ao finalizar, mesclar catálogo completo de perícias básicas WFRP com advances 0 (Foundry `allBasicSkills`), alinhado à expansão futura de `skills.py`.

### 7. Pertences

**Decisão:** Copiar `trappings` da carreira + dinheiro inicial (ex.: 50 GC equivalente em itens de moeda se modelado; senão item “Bolsa de moedas” com descrição).

Sem customização de pertences na criação.

### 8. Cálculo de ferimentos

```python
def strength_bonus(s: int) -> int: return s // 10
def toughness_bonus(t: int) -> int: return t // 10
wounds_max = strength_bonus(S) + toughness_bonus(T)  # mín. 1
```

Remover inputs manuais de `wounds_max` da UI.

### 9. XP de criação

```python
creation_xp = xp_from_species + xp_from_career + xp_from_characteristics
xp_spent = attr_advances * 10 + skill_points_from_optional_purchases  # se houver
xp_total = creation_xp  # personagem começa com XP não gasta = creation_xp - xp_spent
```

Alinhar com Foundry: XP de rolagens é **ganho** e pode ser **gasto** em avanços na mesma criação.

### 10. API

```
GET  /api/rules/character-creation
     → { species, xp_awards, skill_rules, attribute_rules }

GET  /api/rules/careers?tier=1
     → { careers: [{ id, name, class, career_group }] }

GET  /api/rules/careers/{id}
     → career detail

POST /api/characters/validate-creation
     body: CharacterCreationDraft
     → { valid, errors: [{ step, field, message }], computed: CharacterPreview }

POST /api/characters
     body: CharacterCreationSubmit (draft + confirm)
     → CharacterOut

POST /api/characters/generate-background
     body: BackgroundGenerateRequest (draft snapshot + optional hints)
     → { background: string }
```

### 11. UI — wizard

```
/character
  [Pré-gerados] | [Criar personagem]
  
  Stepper: Espécie → Carreira → Atributos → Perícias → Pertences → Detalhes
  Footer: Voltar | Continuar (disabled se invalid)
  Revisão final: resumo somente leitura + Confirmar
```

Reutilizar `AttributeCards` na etapa de revisão (já existente).

Estilo: `card-wfrp`, `tab-btn`, paleta grimório (`Docs/ux-spec.md`).

### 12. Migração do custom legado

- Remover formulário livre de `/character`
- `CharacterCreate` schema deprecated → `CharacterCreationSubmit`
- Pregens inalterados
- Personagens já criados via custom inválido: **não migrar** (projeto pessoal)

### 13. Background gerado por IA

**Decisão:** Endpoint dedicado `POST /characters/generate-background` na etapa Detalhes do wizard. Reutiliza `get_llm_adapter()` (DeepSeek / Anthropic / mock) com system prompt **separado** do GM — arquivo `Docs/character-background-prompt.md`, carregado por `load_character_background_prompt()` em `llm/prompts.py`.

**Prompt (resumo):**

- Persona: escritor de fichas WFRP4e, não mestre de jogo.
- Tom: grim, perilous, Old World, PT-BR.
- Entrada (user message): JSON ou texto estruturado com `name`, `species`, `career`, `talents[]`, resumo de `skills`, `trappings[]`, `hints` opcional.
- Saída: 1–3 parágrafos curtos (~150–400 palavras), **somente** história pessoal; sem tags `[TESTE]`, sem stats, sem meta-comentário.
- Proibir: inventar números, perícias ou itens não presentes no contexto.

**Fluxo UI:**

```
[ Background textarea                    ]
[ Dicas para a IA (opcional)           ]
[ Gerar com IA ]  [ spinner | erro ]
```

- Ao sucesso: preenche textarea; jogador pode editar.
- Regenerar substitui o texto (confirmar se já houver conteúdo manual — opcional MVP: sobrescrever direto).
- Falha LLM: mensagem PT-BR; manual permanece.

**Mock (`LLM_PROVIDER=mock`):**

- `MockLLMAdapter` detecta system prompt de background (ou rota dedicada no service) e retorna texto fixo citando `career` e `name` do payload — sem chamar rede.

**Alternativa rejeitada:** Usar `GMOrchestrator` / `gm-system-prompt.md` — poluiria contexto de sinais e campanha; fora de escopo de criação.

**Alternativa rejeitada:** Geração no frontend chamando API LLM diretamente — expõe chaves e bypassa controle de prompt.

```
POST /api/characters/generate-background
body: {
  "name": "Helena",
  "species": "human",
  "career": "Soldado",
  "talents": ["Resolução"],
  "skills_summary": "Luta +8, Atletismo +5",
  "hints": "veterana da guerra contra o Caos"
}
→ { "background": "..." }
```

---

## Data model (sem migration obrigatória)

Campos opcionais novos em `PlayerCharacter` (JSON ou colunas):

```python
species: str = "human"
subspecies: str | None = "reikland"
creation_method: dict  # { attributes: "roll"|"allocate", species: "roll"|"choose", ... }
```

Alternativa: guardar só em `background` metadata — preferir coluna `species` string para filtros futuros.

---

## Testing strategy

| Camada | Casos |
|--------|--------|
| Unit | rolagem 2d10+20, swap, reroll limits, point-buy 4–18, career XP awards, 40 skill points, wounds/fate derived |
| API | validate-creation 422/200, POST character happy path, generate-background mock, reject invalid |
| E2E | opcional: wizard completo com escolhas (sem rolagem aleatória) |

---

## Sequência de entrega (tasks.md)

1. Catálogos (species + careers Core PT-BR)
2. `character_creation.py` + testes
3. API endpoints
4. Wizard UI etapas 1–3
5. Wizard etapas 4–6 + persistência
6. E2E + remoção custom legado
