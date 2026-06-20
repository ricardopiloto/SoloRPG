# Tasks: Percepção obrigatória no GM + tratativa de rolagens não solicitadas

## 1. Atualizar system prompt do GM — percepção passiva

- [x] 1.1 Em `Docs/gm-system-prompt.md`, adicionar seção "TESTES PASSIVOS DE PERCEPÇÃO E INTUIÇÃO" logo após a seção "FLUXO DE TESTES" com lista de gatilhos obrigatórios
- [x] 1.2 Gatilhos que DEVEM gerar `[TESTE]` de Percepção (Int/Percepção, modificador contextual):
  - Alguém seguindo o personagem por mais de uma cena
  - Detalhe visual ou auditivo fora do lugar em uma cena
  - NPC mentindo ou ocultando informação relevante (→ teste de Intuição/Fel)
  - Possível emboscada ou perigo iminente não declarado
  - Objeto escondido em área que o personagem examina
- [x] 1.3 Adicionar instrução: esses testes são emitidos PELO GM, sem que o jogador precise pedir — são testes reativos ao mundo, não declarados
- [x] 1.4 Adicionar que sucesso REVELA o detalhe narrativamente; falha NÃO REVELA e o GM não indica que havia algo a ver

## 2. Atualizar system prompt do GM — unsolicited rolls

- [x] 2.1 Adicionar regra de conduta #13 em `Docs/gm-system-prompt.md`: reação ao dado espontâneo sem retroativamente inventar situação
- [x] 2.2 `backend/app/llm/prompts.py` carrega `gm-system-prompt.md` automaticamente — nenhuma mudança necessária no código (o arquivo `.md` é a fonte)

## 3. Quick-roll: injetar nota no contexto do próximo turno

- [x] 3.1 Em `gm_orchestrator.execute_quick_roll`, após resolver o teste, persistir no histórico da sessão a nota: "[NOTA DO SISTEMA] O jogador verificou [atributo/perícia] espontaneamente — resultado: [sucesso/falha]"
- [x] 3.2 Nota persistida via `append_turn(db, session, "system", spontaneous_note, {...})` (já suportado)
- [x] 3.3 GM recebe nota no histórico recente e responde narrativamente ao gesto físico sem criar situação retroativa

## 4. Atualizar documentação

- [ ] 4.1 Atualizar `Docs/development-order.md` referenciando esta change
- [ ] 4.2 Rodar pytest para garantir que testes de API não regrediram

## 5. Testes e validação

- [ ] 5.1 Teste manual: iniciar sessão com LLM_PROVIDER=mock, verificar que quick-roll gera entrada no histórico
- [ ] 5.2 Teste com DeepSeek: cena de taverna com NPC suspeito deve gerar [TESTE] de Intuição automaticamente
