# Tasks: add-fate-fortune-mechanics

## 1. Regras backend — Destino

- [x] 1.1 Estender `spend_fate_point()` com motivo `avoid_wound` | `avoid_death` e efeitos distintos
- [x] 1.2 Atualizar `_handle_system_action` para processar `motivo` em `usar_ponto_destino`
- [x] 1.3 Garantir que Destino nunca é restaurado automaticamente (validar `end_session`, progressão)

## 2. Regras backend — Fortuna

- [x] 2.1 Remover efeito `bonus_teste` (+10) de `spend_fortune_point()` — somente `reroll`
- [x] 2.2 Implementar endpoint ou fluxo de re-roll com gasto de Fortuna em teste GM pendente
- [x] 2.3 Rejeitar gasto de Fortuna quando `fortune_current = 0` ou sem teste pendente

## 3. Refresh por sessão

- [x] 3.1 Em `start_session()` (sessão nova): `fortune_current = fortune_max = fate_current`
- [x] 3.2 Sessão pausada retomada: não recalcular Fortuna
- [x] 3.3 Remover `fortune_max` independente em `create_character()` e pregens — derivar de `fate_max` inicial

## 4. API e schemas

- [x] 4.1 Documentar payload `usar_ponto_destino.motivo` e `usar_ponto_fortuna.efeito=reroll` no GM prompt
- [x] 4.2 Expor endpoint de re-roll com Fortuna (se necessário) e incluir `fortune_*` nas respostas de personagem/sessão

## 5. Frontend

- [x] 5.1 Exibir Fortuna na sidebar (gemas separadas de Destino)
- [x] 5.2 Remover input de Fortuna na criação de personagem (`character/page.tsx`)
- [x] 5.3 Oferecer "Gastar Ponto de Fortuna" em teste falho quando `fortune_current > 0`
- [x] 5.4 i18n: labels `character.fortunePoints` em `pt-BR.json`

## 6. GM e memória

- [x] 6.1 Atualizar `Docs/gm-system-prompt.md` com regras Destino vs. Fortuna
- [x] 6.2 Atualizar bloco XML `<pontos_de_destino>` em `memory.py` se necessário

## 7. Testes

- [x] 7.1 Teste: `avoid_wound` deduz Destino sem alterar wounds
- [x] 7.2 Teste: `avoid_death` deduz Destino e define 1 wound
- [x] 7.3 Teste: `start_session` refresh Fortuna = `fate_current`
- [x] 7.4 Teste: sessão pausada não refresh Fortuna
- [x] 7.5 Teste: re-roll com Fortuna deduz 1 e executa nova rolagem
- [x] 7.6 Teste: Fortuna indisponível bloqueia re-roll

## 8. Validação manual

- [ ] 8.1 Personagem 3 Destino → nova sessão mostra 3 Fortuna
- [ ] 8.2 Gastar 1 Destino → próxima sessão mostra 2 Fortuna
- [ ] 8.3 Falha teste + Fortuna → re-roll funciona; gemas Fortuna atualizam
- [ ] 8.4 Golpe mortal + Destino → sobrevive com 1 wound; Destino -1 permanente
