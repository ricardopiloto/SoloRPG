# Tasks: defer-gm-narrative-presentation

## Fase 1 — Backend: sanitização de sinais

- [x] **T1** Adicionar `strip_signal_artifacts()` em `signals.py` (pós-parser, patterns tolerantes)
- [x] **T2** Pattern loose para `[NOVA_CAMPANHA]` com fechamento typo (`[/NOVA_CAMAPANHA]`, case-insensitive)
- [x] **T3** Integrar strip em `stream_turn`, `stream_narrate_roll`, `process_turn`, `execute_roll` narrate — narrative retornado sempre sanitizado
- [x] **T4** Remover fallbacks `parsed.narrative or llm_text` / `or narrative` que reexpõem bruto
- [x] **T5** Testes: `test_signals.py` — NOVA_CAMPANHA typo, MUSICA removido, prosa com colchetes preservada

## Fase 2 — Frontend: apresentação diferida

- [x] **T6** `useSessionPlay`: não criar `ChatEntry` narrative em eventos `token`
- [x] **T7** `useSessionPlay`: no `done`, append narrativa final única (substituir lógica trim streaming)
- [x] **T8** i18n `session.preparingResponse` = "Preparando a resposta…"
- [x] **T9** UI sessão: indicador preparing visível no chat enquanto `loading && !diceRolling`
- [x] **T10** Testes unitários ou integração leve: tokens ignorados, done revela narrativa

## Fase 3 — Prompt e docs

- [x] **T11** `gm-system-prompt.md`: reforçar tags de fechamento exatas; sinais invisíveis ao jogador
- [x] **T12** Atualizar `CHANGELOG.md` (Unreleased) e nota breve se aplicável

## Fase 4 — Validação manual

- [ ] **T13** Primeira sessão: `[NOVA_CAMPANHA]` não aparece no chat (nem durante streaming nem após)
- [ ] **T14** Turno com `[MUSICA]` + `[TESTE]`: jogador vê preparing → narrativa limpa → UI de teste/mood/imagem
- [ ] **T15** Histórico de sessão recarregado: turnos antigos sem vazamento de JSON

## Dependências

- T1–T5 antes de T13–T15 (leak NOVA_CAMPANHA)
- T6–T9 antes de T13–T14 (streaming UX)
- T11 pode paralelizar com T1–T10
