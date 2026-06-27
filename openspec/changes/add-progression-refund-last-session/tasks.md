# Tasks: add-progression-refund-last-session

## Fase 1 — Modelo e janela de sessão

- [x] **T1** Migration: `progression_source_session_id`, `progression_refund_budget`, `progression_purchases` em `PlayerCharacter`
- [x] **T2** `end_session()`: abrir janela (`source_session_id`, `refund_budget = xp_awarded`, limpar purchases)
- [x] **T3** `start_session()`: fechar janela (zerar campos — compras não reembolsáveis)

## Fase 2 — Regras e serviços

- [x] **T4** `reverse_skill_advance()` e `reverse_talent()` em `careers.py`
- [x] **T5** `purchase_skill_advance()` / `purchase_talent()`: append ledger + atribuição FIFO
- [x] **T6** `refund_progression_purchase()`: validações + reversão + `xp_spent` + restaurar budget
- [x] **T7** `get_progression_options()`: expor `refundable_purchases`, `refund_budget_remaining`, `progression_window_active`

## Fase 3 — API

- [x] **T8** Schemas `ProgressionPurchaseOut`, `ProgressionRefundIn`; estender `ProgressionOptionsOut`
- [x] **T9** `POST /characters/{id}/progression/refund`
- [x] **T10** Testes integração: compra reembolsável, devolução, budget FIFO, bloqueio pós-nova-sessão, talento

## Fase 4 — Frontend

- [x] **T11** `api.refundPurchase()` + tipos em `api.ts`
- [x] **T12** Seção "Compras desta sessão" em `progression/page.tsx` com botão Devolver
- [x] **T13** i18n PT-BR (`progression.refund`, `progression.refundSection`, `progression.refundBudget`)

## Fase 5 — Docs e validação

- [x] **T14** `CHANGELOG.md` (Unreleased)
- [x] **T15** `openspec validate add-progression-refund-last-session --strict`

## Fase 6 — Validação manual

- [ ] **T16** Encerrar sessão → comprar perícia por engano → Devolver → XP e contador corretos
- [ ] **T17** Esgotar budget reembolsável → compra extra sem botão Devolver
- [ ] **T18** Iniciar nova sessão → devolução bloqueada na API

## Dependências

- T1 → T2–T3 → T5–T6
- T4 antes de T6
- T7–T9 antes de T11–T12
- T10 após T2–T9
