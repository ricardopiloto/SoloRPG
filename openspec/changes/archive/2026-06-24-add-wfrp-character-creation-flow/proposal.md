# Proposal: add-wfrp-character-creation-flow

**Data:** 2026-06-21  
**Status:** Draft  
**Relacionado:** `add-wfrp-solo-mvp` (requisito de criação customizada não implementado de fato), `add-fate-fortune-mechanics` (Destino/Fortuna na criação), `update-character-sidebar-stats-ui` (catálogo de perícias parcial)

---

## Why

A página `/character` hoje oferece dois caminhos:

1. **Pré-gerados** — dois templates válidos, funcionais.
2. **Customizado** — formulário livre que aceita atributos, ferimentos e Destino arbitrários **sem validação WFRP4e**.

O requisito arquivado em `character-management` (“validates the character against WFRP4e creation rules”) nunca foi cumprido. O jogador pode criar personagens inválidos (ex.: WS 60, 20 ferimentos, zero perícias de carreira), quebrando combate, progressão e coerência narrativa.

Referência de implementação: o sistema [WFRP4e-FoundryVTT](https://github.com/moo-man/WFRP4e-FoundryVTT) (`src/apps/chargen/`) implementa um assistente em etapas alinhado ao livro de regras — espécie → carreira → atributos → perícias/talentos → pertences → detalhes.

---

## What Changes

Substituir o formulário “customizado” por um **fluxo guiado em etapas** com validação **server-side** determinística, espelhando as regras do livro base WFRP4e (Cubicle 7) e o comportamento do Foundry VTT.

### Etapas do assistente (espelho Foundry `char-gen.js`)

| # | Etapa | Regras principais |
|---|--------|-------------------|
| 1 | **Espécie** | MVP: Humano (Reikland). Escolher (0 XP bônus) ou rolar na tabela (+20 XP bônus de criação). |
| 2 | **Carreira** | Escolher ou rolar carreira Tier 1 do catálogo Core. Rolagens: +50 XP (1ª), +25 XP (2ª leva), depois 0. |
| 3 | **Atributos** | Rolar `2d10+20` por atributo **ou** comprar com 100 pontos (4–18 cada, antes do bônus de espécie). Trocar dois valores; rerrolar tudo uma vez. Avanços de atributo na criação: máx. 5 totais (10 XP cada, do pool de XP de criação). Alocar Pontos de Destino a partir do pool `extra` da espécie. |
| 4 | **Perícias e talentos** | Perícias de espécie: até 3 em +3 e 3 em +5. Perícias de carreira: distribuir 40 pontos (máx. 10 por perícia). Escolher 1 talento de carreira; resolver talentos aleatórios/de escolha da espécie. |
| 5 | **Pertences** | Aplicar automaticamente os *trappings* da carreira Tier 1 (+ moeda inicial padrão). |
| 6 | **Detalhes e revisão** | Nome, background (manual **ou gerado por IA**), motivações; revisão da ficha; persistência. |

### Geração de background com IA (etapa Detalhes)

Na etapa **Detalhes**, o campo Background oferece:

- **Escrita manual** — textarea editável (comportamento atual).
- **Gerar com IA** — botão que chama o backend; usa o **mesmo adapter LLM** da aplicação (`get_llm_adapter()` / DeepSeek ou mock), **sem** o system prompt do GM.

O prompt dedicado (`Docs/character-background-prompt.md`) instrui a LLM a produzir um parágrafo curto de história pessoal em PT-BR, tom grim & perilous, alinhado ao universo WFRP4e, usando apenas contexto mecânico já definido (nome, espécie, carreira, talentos, pertences — **sem inventar stats**).

| Aspecto | Decisão |
|---------|---------|
| Endpoint | `POST /characters/generate-background` |
| Input | snapshot do rascunho (`name`, `species`, `career`, `talents`, `skills` resumidas, `hints` opcional do jogador) |
| Output | `{ background: string }` — texto puro, sem sinais GM |
| Edição | Jogador pode editar/regenerar antes de confirmar |
| Mecânica | LLM **não** altera atributos, perícias ou validação — só o campo `background` |
| Testes | Mock adapter retorna background determinístico; teste API com `LLM_PROVIDER=mock` |

### Derivados calculados no backend (não editáveis pelo jogador)

- `wounds_max` = Bônus de Força + Bônus de Resistência (Humano)
- `fate_max` / `fate_current` = base da espécie + pontos alocados
- `fortune_*` = derivado de `fate_*` (regra `add-fate-fortune-mechanics`)
- Perícias básicas do sistema adicionadas automaticamente (advances 0)
- `xp_total` = soma do XP “gasto” em rolagens durante a criação (regra WFRP: escolhas aleatórias concedem XP para gastar em avanços)
- `xp_spent` = avanços de atributo/perícia comprados na criação

### Backend

- Módulo `backend/app/rules/character_creation.py` — rolagens, validação, derivados, XP de criação
- Catálogo estático `backend/app/rules/careers_catalog.py` (ou JSON) — carreiras Tier 1 do Core em PT-BR: perícias, talentos, pertences, tabela de rolagem Humano
- Catálogo de espécies `backend/app/rules/species.py` — Humano/Reiklander no MVP
- Endpoints:
  - `GET /rules/character-creation` — constantes e opções de criação
  - `GET /rules/careers` — lista Tier 1
  - `GET /rules/careers/{career_id}` — detalhe
  - `POST /characters/validate-creation` — valida rascunho, retorna erros + ficha calculada
  - `POST /characters/generate-background` — gera texto de background via LLM (prompt dedicado, não-GM)
  - `POST /characters` — aceita apenas payload validado (quebra API livre atual do custom)
- Testes unitários extensivos em `test_character_creation.py`

### Frontend

- Substituir aba “Customizado” por wizard multi-step em `/character` (ou `/character/create`)
- Estado do rascunho no cliente; validação incremental via API
- Componentes reutilizáveis: rolagem de atributos (com swap), alocador de perícias, seletor de carreira
- Etapa Detalhes: textarea de background + botão **Gerar com IA** (loading/erro); campo `hints` opcional para orientar a IA
- i18n PT-BR para todas as strings do fluxo
- Manter aba **Pré-gerados** inalterada

---

## Capabilities

### New Capabilities

- `character-creation`: regras WFRP4e de criação, catálogos, validação, persistência e geração narrativa de background.

### Modified Capabilities

- `character-management`: substituir criação customizada livre por fluxo validado; background opcional via IA.
- `wfrp-rules-engine`: adicionar motor de criação e cálculo de derivados.
- `web-interface`: wizard de criação em etapas com ação “Gerar background com IA”.

---

## Não-escopo (nesta change)

- Espécies além de Humano (Anão, Elfo, Halfling, etc.) — follow-up `add-species-character-creation`
- Resiliência, Movimento, Marcas Arcanas — não usados pelo motor de jogo atual
- Insanidade/Corrupção
- Editor de personagem pós-criação
- Importar compendiums Cubicle 7 / Foundry diretamente (dados reimplementados em JSON próprio por licenciamento)
- Expansões além do Core Rulebook (Up in Arms, etc.)

---

## Impacto

| Área | Alterações |
|------|------------|
| Backend | `rules/character_creation.py`, `rules/species.py`, `rules/careers_catalog.py`, `services/character.py`, `llm/prompts.py`, `Docs/character-background-prompt.md`, `schemas/api.py`, `routes.py` |
| Frontend | `app/character/page.tsx`, novos componentes em `components/character-creation/` |
| Dados | Catálogo Core careers/skills/talents PT-BR |
| Testes | `test_character_creation.py`, atualizar `test_api_integration.py`, E2E `game-loop.spec.ts` |
| Docs | Referência cruzada com Foundry chargen; nota de licenciamento de conteúdo |

---

## Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| Volume de dados (60+ carreiras Core) | JSON modular; gerar a partir de planilha; entregar Core completo em tasks fatiadas |
| Divergência livro vs Foundry | Foundry como referência de algoritmo; regra do livro prevalece em conflito documentado |
| Breaking change em `POST /characters` | Manter pregens; custom antigo removido da UI; API rejeita payload não validado com 422 |
| LLM inventar mecânicas no background | Prompt proíbe alterar stats; output só texto; jogador revisa antes de salvar |
| Falha de API LLM na geração | Erro amigável na UI; escrita manual continua disponível |

---

## Referências

- [WFRP4e-FoundryVTT — `src/apps/chargen/`](https://github.com/moo-man/WFRP4e-FoundryVTT/tree/master/src/apps/chargen)
- `Docs/product-brief.md` §7.2
- `openspec/changes/add-wfrp-solo-mvp/specs/character-management/spec.md`
