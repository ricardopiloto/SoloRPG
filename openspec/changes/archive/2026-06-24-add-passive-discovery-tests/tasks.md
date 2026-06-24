# Tasks: add-passive-discovery-tests

## Fase 1 — Atualização do prompt

- [x] **T1** Em `Docs/gm-system-prompt.md`, dentro da seção `FLUXO DE TESTES`, adicionado bloco `TIPO 3 — TESTE PASSIVO DE DESCOBERTA` após o bloco TIPO 2
- [x] **T2** 3 exemplos concretos adicionados: percepção auditiva (respiração no portal), visual (rua estranha), conhecimento contextual (runas na parede)
- [x] **T3** Versão atualizada para `2.5`

## Validação manual

- [ ] **T4** Iniciar sessão nova e observar se o GM começa a emitir testes passivos organicamente em momentos sensoriais
- [ ] **T5** Verificar que o [TESTE] emitido tem `obrigatorio: false` e `opcao_alternativa: null` nesses casos
- [ ] **T6** Confirmar que a história avança normalmente após a rolagem (seja sucesso ou falha)
