# Tasks: enforce-inventory-constraints

## Fase 1 — Regra de prompt (sem código, impacto imediato)

- [x] **1.1** Adicionar seção `RESTRIÇÕES DE INVENTÁRIO` ao `Docs/gm-system-prompt.md`
  - Regra: GM só permite uso de itens presentes em `<inventario>`
  - Regra: negar narrativamente dentro do mundo (nunca quebrar personagem)
  - Regra: itens do cenário podem ser usados contextualmente, mas requerem `[ACAO_SISTEMA]` para aquisição permanente
  - Exemplos ERRADO vs CORRETO análogos ao padrão de sinal
  - Adicionado como item 17 em "REGRAS DE CONDUTA ABSOLUTAS"

## Fase 2 — Backend guard heurístico

- [x] **2.1** Implementar `_check_inventory_reference(action: str, trappings: list[dict]) -> str | None` em `gm_orchestrator.py`
  - Normaliza action e nomes de trappings (lowercase, remoção de acentos via unicodedata)
  - Lista de formas verbais cobre infinitivos + conjugações comuns (1ª/3ª pessoa, passado)
  - Retorna nota de sistema se item não encontrado, `None` caso contrário
  - Filtra preposições/artigos antes do match de candidato

- [x] **2.2** Integrado em `process_turn()` — nota injetada antes de `"Ação do jogador:"` quando detectado

- [x] **2.3** Integrado em `stream_turn()` — mesma lógica que 2.2

- [x] **2.4** Não integrado em `narrate_roll()` / `stream_narrate_roll()` — conforme especificado

## Fase 3 — Testes

- [x] **3.1** Testes unitários em `tests/test_inventory_guard.py` (10 casos):
  - Item presente → `None` ✓
  - Item ausente → nota com inventário ✓
  - Sem verbo de uso → `None` ✓
  - Normalização de acentos (match e ausente) ✓
  - Inventário vazio com verbo → nota "(inventário vazio)" ✓
  - Case-insensitive ✓
  - Nota contém lista completa de inventário ✓
  - Verbo "beber" com item ausente ✓

- [x] **3.2** Testes de integração em `tests/test_inventory_guard.py` (2 casos):
  - `POST /sessions/{id}/turn` com item ausente → 200 ✓
  - `POST /sessions/{id}/turn` com item presente → 200 ✓

## Validação manual

- [ ] **4.1** Sessão real com personagem que tem apenas espada curta: digitar "saco minha espada longa" → GM nega narrativamente
- [ ] **4.2** Personagem com espada longa: "empunho minha espada longa" → GM narra normalmente
- [ ] **4.3** Personagem sem armas: "ato uma pedra do chão e lanço" → GM permite (item do cenário, sem verbo de inventário)
