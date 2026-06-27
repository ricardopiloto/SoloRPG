# Tasks: add-gm-social-test-triggers

## Fase 1 — Catálogo Intuição

- [x] **T1** Adicionar `"Intuição": "I"` em `SKILL_CATALOG` (`backend/app/rules/skills.py`)
- [x] **T2** Incluir `Intuição` em `PROGRESSION_SKILL_NAMES`
- [x] **T3** Teste unitário: `list_skills()` contém Intuição com `linked_attribute: I`
- [x] **T4** Teste: quick-roll com perícia `Intuição` não retorna erro de perícia inválida

## Fase 2 — Prompt: gatilhos sociais

- [x] **T5** Estender tabela `GATILHOS OBRIGATÓRIOS DE TESTE` com Charme e Intuição
- [x] **T6** Anti-padrão + fluxo correto: extrair informações da dona da taverna → Charme
- [x] **T7** Anti-padrão + fluxo correto: "percebo se ele está mentindo?" → Intuição
- [x] **T8** Modificadores contextuais sugeridos (Charme e Intuição)
- [x] **T9** Exemplos JSON completos para ambos os gatilhos
- [x] **T10** Atualizar exceção do critério geral (+ interações sociais contestadas)
- [x] **T11** Nota TIPO 1 vs TIPO 3 para Intuição (contestado vs passivo)

## Fase 3 — Specs e docs

- [x] **T12** Spec deltas `synthetic-gm`, `gm-narrative`, `wfrp-rules-engine`
- [x] **T13** Atualizar `CHANGELOG.md` (Unreleased)
- [x] **T14** `openspec validate add-gm-social-test-triggers --strict`

## Fase 4 — Validação manual

- [ ] **T15** Jogador pede mais informações a NPC → `[TESTE]` Charme antes de revelar segredo
- [ ] **T16** Jogador pergunta se NPC mente → `[TESTE]` Intuição antes de confirmar
- [ ] **T17** Sidebar/quick-roll lista e rola Intuição

## Dependências

- T1–T4 antes de T17
- T5–T11 podem paralelizar com T1–T4
- T12–T14 após T1–T11
- T15–T16 após prompt merge
