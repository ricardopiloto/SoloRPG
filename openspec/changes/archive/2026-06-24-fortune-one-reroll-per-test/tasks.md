# Tasks: fortune-one-reroll-per-test

## 1. Backend — estado do teste

- [x] 1.1 Inicializar `fortune_reroll_used: false` em `pending_roll_result` no `execute_roll()`
- [x] 1.2 Setar `fortune_reroll_used: true` após `execute_fortune_reroll()` bem-sucedido
- [x] 1.3 Rejeitar `execute_fortune_reroll()` quando `fortune_reroll_used` já é `true`

## 2. API

- [x] 2.1 Adicionar `fortune_reroll_available: bool` em `RollResponse`
- [x] 2.2 Calcular em `_roll_response()`: falhou && fortune > 0 && !fortune_reroll_used

## 3. Frontend

- [x] 3.1 Usar `fortune_reroll_available` em vez de só `fortune_current > 0` após falha
- [x] 3.2 Após re-roll falho, não reexibir prompt de Fortuna (ir direto para continuar/narrar)

## 4. Testes

- [x] 4.1 Teste: primeira falha permite fortune reroll
- [x] 4.2 Teste: segundo fortune reroll no mesmo teste rejeitado
- [x] 4.3 Teste: `fortune_reroll_available=false` após reroll usado

## 5. Validação manual

- [ ] 5.1 Falhar teste → re-roll com Fortuna → falhar de novo → sem botão Fortuna
- [ ] 5.2 Novo teste GM → botão Fortuna disponível novamente (se houver Fortuna)
