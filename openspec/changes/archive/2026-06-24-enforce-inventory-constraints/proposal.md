# Proposal: enforce-inventory-constraints

**Data:** 2026-06-23  
**Status:** Draft  
**Relacionado:** `add-wfrp-solo-mvp` (inventário no contexto), `sync-gm-prompt-v23` (system prompt GM)

---

## Why

O GM sintético recebe o inventário completo do personagem via `<inventario>` no context XML a cada turno, mas **não tem instrução explícita** para bloquear o uso de itens ausentes. Resultado: o LLM frequentemente aceita e narra ações que dependem de itens que o personagem não possui ("Você saca a espada longa e..." quando a ficha tem apenas um facão), quebrando a verossimilhança mecânica e possibilitando vantagem indevida.

A solução segue a arquitetura existente do projeto: **regra no prompt** (instrução ao GM) reforçada por uma **injeção determinística de backend** (nota de sistema quando detecção heurística identifica referência a item ausente).

---

## What Changes

### Camada 1 — System Prompt (regra GM)

Nova seção adicionada ao `Docs/gm-system-prompt.md` com regra explícita:

- O GM **somente** permite que o personagem use, saque, equipe ou mencione fisicamente itens que aparecem em `<inventario>`.
- Se o jogador citar um item ausente, o GM deve **negar narrativamente dentro do mundo** — nunca quebrando personagem, nunca explicando que é uma regra do sistema.
- Itens consumíveis usados (poções, flechas contadas, etc.) podem ser marcados como esgotados narrativamente e o GM não os permite novamente na mesma sessão sem reposição narrada.
- Itens do cenário (uma tocha na parede, uma espada caída de um inimigo) **podem** ser usados contexto-narrativamente, mas devem ser adicionados ao inventário via sinal `[ACAO_SISTEMA]` antes de qualquer uso subsequente.

### Camada 2 — Backend guard (injeção heurística)

Em `gm_orchestrator.py`, antes de montar a mensagem ao LLM, uma função heurística analisa o texto da ação do jogador:

1. Detecta padrões de uso/saque/equipamento de item (verbos: sacar, usar, pegar, empunhar, atirar, lançar, etc. + substantivo).
2. Compara contra a lista de `character.trappings`.
3. Se o item referenciado não for encontrado no inventário, injeta uma `[NOTA DO SISTEMA]` na mensagem ao LLM **antes** da ação do jogador:

```
[NOTA DO SISTEMA — INVENTÁRIO] O jogador mencionou "<item>". Este item NÃO consta no inventário do personagem: {lista_inventario}. Negue o uso narrativamente dentro do universo do jogo sem quebrar personagem.
```

4. Se o item for encontrado no inventário, não injeta nada (fluxo normal).

A detecção é **heurística, não semântica** — usa normalização de texto (remoção de acentos, lowercase) e substring matching. Falsos negativos (item mencionado de outra forma) são aceitáveis — a regra de prompt garante o comportamento esperado na maioria dos casos; a injeção de backend é um reforço determinístico para os casos mais óbvios.

---

## Capabilities

### Modified Capabilities

- **gm-narrative** (`openspec/specs/session-lifecycle/`): o GM passa a ter restrição explícita de inventário como regra de conduta
- **session-lifecycle**: pré-processamento do turno do jogador adiciona verificação heurística de itens

### New Capabilities

- **inventory-prompt-rule**: regra de inventário no system prompt do GM
- **inventory-backend-guard**: injeção de nota de sistema quando item ausente é detectado na ação do jogador

---

## Impact

| Área | Alterações |
|------|------------|
| `Docs/gm-system-prompt.md` | Nova seção "RESTRIÇÕES DE INVENTÁRIO" nas Regras de Conduta Absolutas |
| `backend/app/services/gm_orchestrator.py` | Função `_check_inventory_reference()` chamada em `process_turn()` e `stream_turn()` antes de montar mensagens |
| `backend/tests/` | Testes unitários para a função de detecção heurística; testes de integração com mock LLM |

---

## Non-Goals

- NLP semântica ou modelo de linguagem para detecção de itens — heurística simples é suficiente para MVP
- Rastreamento automático de consumo de itens (flechas, poções) — o GM narra, não o backend
- Modificação do inventário via chat — continua sendo feito pela tela de personagem
- Itens criados/achados durante a sessão sendo adicionados automaticamente ao banco — permanece via UI

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| Heurística de substring para detecção | NLP semântico / embedding | Complexidade e latência adicionais não justificadas no MVP |
| Injeção como `[NOTA DO SISTEMA]` no contexto existente | Novo campo no XML de contexto | Padrão já utilizado em outros pontos do orchestrator (quick_roll, etc.) |
| Detecção apenas em `process_turn`/`stream_turn` | Também em `narrate_roll` | Ações de item ocorrem no turno inicial, não na narração de resultado |

---

## Open Questions (defaults assumidos)

| Questão | Decisão |
|---------|---------|
| O que fazer com itens do cenário (tocha na parede)? | Permitidos contextualmente; GM narra aquisição e adiciona via `[ACAO_SISTEMA]` se relevante |
| Itens sem nome no inventário (ex: "equipamentos gerais")? | Agrupamentos genéricos permitem uso de qualquer item razoável compatível com o grupo |
| Falso positivo do heurístico (item presente mas não reconhecido)? | Aceitável — a nota de sistema pede ao GM para negar; o GM pode ignorar a nota se o contexto narrativo justificar |
