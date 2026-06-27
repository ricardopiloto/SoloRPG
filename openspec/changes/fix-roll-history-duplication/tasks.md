# Tasks: fix-roll-history-duplication

## Fase 1 — Corrigir duplicação no fluxo roll → narrate

- [x] **T1** Remover chamada `appendRolls(result.roll_results)` de `applyMeta()` em `useSessionPlay.ts`
- [x] **T2** Confirmar que `applyRollResponse` e quick-roll em `handleDiceRollComplete` permanecem como únicos pontos de append para rolagens ao vivo
- [x] **T3** Verificar fluxo Fortuna re-roll: 1 append por `/roll` ou `/fortune-reroll`, sem eco no narrate

## Fase 2 — Restaurar histórico ao carregar sessão

- [x] **T4** Extrair `buildRollHistoryFromTurns(turns)` (helper testável) mapeando `metadata.rolls` e `metadata.quick_roll`
- [x] **T5** Em `load()`, após `getSessionHistory`, chamar `setRollHistory(buildRollHistoryFromTurns(turns))`
- [x] **T6** Garantir replace (não append) para evitar duplicação em remount

## Fase 3 — Testes e docs

- [x] **T7** Teste unitário: roll + narrate com mesmo `roll_results` → 1 entrada
- [x] **T8** Teste unitário: rebuild de turns mock com 2 gm rolls → 2 entradas
- [x] **T9** Spec delta `session-ui` + `CHANGELOG.md` (Unreleased)
- [x] **T10** `openspec validate fix-roll-history-duplication --strict`

## Fase 4 — Validação manual

- [ ] **T11** Sessão real: 2 testes Percepção → aba Rolagens mostra 2 entradas
- [ ] **T12** Recarregar página → Rolagens mantém contagem correta
- [ ] **T13** Quick-roll espontâneo → 1 entrada com badge "Espontânea"

## Dependências

- T1–T3 antes de T11
- T4–T6 paralelizável com T1–T3
- T7–T8 após T1 e T4
