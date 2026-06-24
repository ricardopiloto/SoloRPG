# Tasks: add-wfrp-character-creation-flow

## 1. Dados — catálogos Core (PT-BR)

- [x] 1.1 `backend/app/rules/species.py` — Humano/Reikland: fórmulas, fate base, extra pool, perícias/talentos de espécie
- [x] 1.2 `backend/app/rules/careers_catalog.json` — estrutura Tier 1 (id, name, class, skills, talents, trappings, roll table)
- [x] 1.3 Popular catálogo com carreiras Core Rulebook (mín. tabela Humano completa; meta: todas Tier 1 Core)
- [x] 1.4 Expandir `skills.py` ou `skills_basic.py` — perícias básicas WFRP necessárias à criação (referência Foundry basic skills)
- [x] 1.5 `GET /rules/character-creation` e `GET /rules/careers` (+ `/{id}`)

## 2. Backend — motor de criação

- [x] 2.1 `backend/app/rules/character_creation.py` — rolagem 2d10+20, swap, reroll, point-buy 4–18
- [x] 2.2 Cálculo derivados: wounds, fate, fortune inicial, bônus de atributo
- [x] 2.3 XP de criação (espécie/carreira/atributos) e gasto em avanços
- [x] 2.4 Alocação perícias espécie (+3/+5 limits) e carreira (40 pts, máx 10/skill)
- [x] 2.5 Seleção talentos (espécie + 1 carreira) e merge trappings
- [x] 2.6 `POST /characters/validate-creation` + schemas `CharacterCreationDraft` / `CharacterCreationSubmit`
- [x] 2.7 Atualizar `POST /characters` — só payload validado; 422 para legado
- [x] 2.8 `test_character_creation.py` — casos felizes e violações por regra

## 2b. Backend — background com IA

- [x] 2b.1 `Docs/character-background-prompt.md` — prompt dedicado WFRP4e (não-GM)
- [x] 2b.2 `load_character_background_prompt()` em `llm/prompts.py`
- [x] 2b.3 `services/character_background.py` — monta user message a partir do rascunho; chama `get_llm_adapter().complete()`
- [x] 2b.4 Mock: resposta determinística quando `LLM_PROVIDER=mock`
- [x] 2b.5 `POST /characters/generate-background` + schema `BackgroundGenerateRequest` / `BackgroundGenerateOut`
- [x] 2b.6 `test_character_background.py` — mock happy path, payload mínimo, erro se name/career ausentes

## 3. Frontend — wizard

- [x] 3.1 Tipos + `api.getCreationOptions()`, `api.listCareers()`, `api.validateCreation()`, `api.createCharacterFromDraft()`
- [x] 3.2 Hook `useCharacterCreation` com persistência opcional em `localStorage`
- [x] 3.3 Componente `CharacterCreationWizard` + stepper
- [x] 3.4 Etapa Espécie (escolher / rolar)
- [x] 3.5 Etapa Carreira (escolher / rolar / lista)
- [x] 3.6 Etapa Atributos (rolagem com swap/reroll OU point-buy)
- [x] 3.7 Etapa Perícias e talentos
- [x] 3.8 Etapa Pertences (read-only) + Detalhes/Revisão (background manual + **Gerar com IA** + hints opcionais)
- [x] 3.9 Substituir aba custom em `character/page.tsx`; manter pregens
- [x] 3.10 i18n `messages/pt-BR.json` — chaves `chargen.*` (incl. `chargen.generateBackground`, `chargen.backgroundHints`, erros LLM)

## 4. Integração e qualidade

- [x] 4.1 Atualizar pregens se necessário para alinhar com catálogo expandido
- [x] 4.2 Atualizar `test_api_integration.py` — criação via wizard payload
- [x] 4.3 Atualizar E2E `game-loop.spec.ts` se fluxo de entrada mudar
- [x] 4.4 `npm run build` + `pytest` verdes
- [ ] 4.5 Manual: criar Soldado rolado, criar Aprendiz point-buy, iniciar campanha e jogar 1 turno
- [ ] 4.6 Manual: gerar background com IA na etapa Detalhes, editar texto, persistir personagem

## 5. Documentação

- [x] 5.1 Nota em `Docs/product-brief.md` ou README: criação segue Core WFRP4e; espécies extras em follow-up
- [x] 5.2 Comentário no código referenciando Foundry `src/apps/chargen/` como referência de algoritmo
- [x] 5.3 Documentar `character-background-prompt.md` no índice `Docs/README.md` (se existir)

## Dependências

- Recomendado após `add-fate-fortune-mechanics` (Destino/Fortuna na criação)
- Independente de `update-character-sidebar-stats-ui` (reutiliza `AttributeCards` na revisão se disponível)

## Paralelizável

- Tasks 1.x (dados) enquanto 2.1–2.3 começam com Humano hardcoded
- Tasks 3.4–3.8 por etapa após API de validate existir
