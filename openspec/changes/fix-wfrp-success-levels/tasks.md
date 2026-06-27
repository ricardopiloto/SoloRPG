# Tasks: fix-wfrp-success-levels

## Fase 1 — Backend: testes e texto

- [x] **T1** Teste unitário: target 32, roll 3 → success, levels == 3
- [x] **T2** Testes adicionais: sucesso marginal (40 vs 34 → 1 nível); falha com margem
- [x] **T3** Melhorar `TestResult.to_llm_text()` — plural `nível` / `níveis` (não `nível(is)`)

## Fase 2 — Frontend: usar levels do servidor

- [x] **T4** Adicionar `levels?: number` em `TurnResponse.roll_results` (`api.ts`)
- [x] **T5** `appendRolls()`: usar `r.levels ?? 1`; remover fórmula `floor((target-roll)/10)`
- [x] **T6** Se `fix-roll-history-duplication` aplicado: `buildRollHistoryFromTurns` mapeia `levels` de metadata

## Fase 3 — UI PT-BR

- [x] **T7** `DiarySidebar`: plural correto via helper ou i18n (`nível` / `níveis`, nunca `nívels`)
- [x] **T8** Chave i18n opcional em `pt-BR.json` (ex.: `session.successLevelCount`)

## Fase 4 — Specs e validação

- [x] **T9** Spec deltas `wfrp-rules-engine` + `session-ui`
- [x] **T10** Teste unitário frontend: `formatSuccessLevels` ou mapeamento rollHistory
- [x] **T11** `CHANGELOG.md` (Unreleased)
- [x] **T12** `openspec validate fix-wfrp-success-levels --strict`

## Fase 5 — Validação manual

- [ ] **T13** Teste GM alvo 32, rolar 3 → aba Rolagens: "Sucesso (3 níveis)"
- [ ] **T14** Quick-roll com 1 nível → texto "1 nível" (singular)

## Dependências

- T1–T3 independentes de T4–T8
- T6 depende de `fix-roll-history-duplication` se em paralelo — coordenar merge
