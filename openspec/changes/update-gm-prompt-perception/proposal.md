# Change: Percepção obrigatória no GM + tratativa de rolagens não solicitadas

## Why

Dois problemas relacionados ao sistema de testes:

1. **Percepção passiva ausente no GM:** O GM atual só solicita testes quando o jogador *age*. Situações em que um personagem notaria algo automaticamente (uma pessoa seguindo-o, um detalhe suspeito em uma cena, um som fora do lugar) não geram testes de Percepção — o GM narra sem o filtro sensorial do personagem. Isso quebra a ficção do WFRP4e, onde Percepção e Intuição são habilidades com valor mecânico real.

2. **Rolagens não solicitadas:** O frontend expõe o painel de quick-roll, permitindo ao jogador rolar dados fora de qualquer contexto solicitado pelo GM. Atualmente o backend lida com isso mas o GM não trata o resultado de forma narrativa — ele ignora ou confunde a rolagem como parte de uma ação normal. Precisa de uma resposta narrativa coerente quando nenhum teste estava pendente.

## What Changes

- **`Docs/gm-system-prompt.md`:** Adicionar seção de testes de percepção passiva com lista de gatilhos obrigatórios (alguém seguindo, detalhe suspeito, emboscada iminente, etc.) e instrução de emitir `[TESTE]` de Percepção/Intuição nesses cenários.
- **`Docs/gm-system-prompt.md`:** Adicionar regra de conduta #13: quando nenhum teste foi solicitado e o resultado de um dado aparece no contexto, o GM deve reconhecer narrativamente que nenhuma ação específica foi pedida.
- **`backend/app/services/gm_orchestrator.py`:** Ao receber resultado de quick-roll (`execute_quick_roll`), injetar no contexto do próximo turno uma nota de que o jogador "verificou [atributo]" espontaneamente, para que o GM possa reagir.
- **`backend/app/api/routes.py`:** Endpoint de quick-roll retorna um `narration_hint` que o frontend já exibe — sem mudança necessária aqui.

## Impact

- Affected specs: `gm-prompt`, `session-ui`
- Affected code:
  - `Docs/gm-system-prompt.md` — novas regras de percepção passiva e unsolicited rolls
  - `backend/app/services/gm_orchestrator.py` — injetar nota de quick-roll no histórico de turno
  - `backend/app/llm/prompts.py` — atualizar hint de contexto
- No breaking changes; somente prompt e lógica de contexto
