# Proposal: add-progression-refund-last-session

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `fix-progression-skill-advance-count`, `character-management`, `improve-session-end-flow`

---

## Why

Na tela **Progressão** (`/progression`), o jogador compra avanços de perícia (+5 XP) e talentos (+10 XP) sem confirmação. Um clique acidental gasta XP de forma irreversível hoje — `xp_spent` só sobe, não há como desfazer.

O jogador precisa **devolver** compras feitas por engano, mas **somente** no contexto da sessão recém-encerrada: o reembolso MUST estar limitado ao XP ganho na **última sessão** (`GameSession.xp_awarded`), não ao pool total de XP acumulado de sessões anteriores.

---

## Estado atual

| Componente | Comportamento |
|------------|---------------|
| `end_session()` | `character.xp_total += session.xp_awarded` |
| `purchase_skill_advance()` | `xp_spent += 5`, incrementa `advances` |
| `purchase_talent()` | `xp_spent += 10`, adiciona talento |
| `/progression` | Botões de compra; sem histórico nem devolução |
| Persistência | Apenas `xp_total` / `xp_spent` — sem ledger de compras |

---

## What Changes

### 1. Ledger de compras pós-sessão (backend)

Novos campos em `PlayerCharacter` (JSON + escalares):

| Campo | Propósito |
|-------|-----------|
| `progression_source_session_id` | UUID da última sessão encerrada que abriu a janela de progressão |
| `progression_refund_budget` | XP da última sessão ainda disponível para atribuição reembolsável (inicia em `xp_awarded`) |
| `progression_purchases` | Lista `[{id, type, skill/talent, cost, refundable_xp, refunded, created_at}]` |

**Ciclo de vida:**

1. **`end_session`:** define `progression_source_session_id`, `progression_refund_budget = xp_awarded`, limpa `progression_purchases`
2. **`start_session` (nova sessão):** zera janela — compras anteriores ficam permanentes
3. **Compra:** registra entrada; `refundable_xp = min(cost, progression_refund_budget)`; decrementa budget
4. **Devolução:** reverte efeito mecânico, `xp_spent -= cost`, restaura budget em `refundable_xp`, marca `refunded: true`

**Atribuição FIFO:** se o jogador tinha XP antigo + XP novo, as primeiras compras consomem o budget reembolsável da última sessão até esgotar; compras posteriores têm `refundable_xp = 0`.

### 2. API

| Endpoint | Ação |
|----------|------|
| `GET /characters/{id}/progression` | Inclui `refundable_purchases[]` e `refund_budget_remaining` |
| `POST /characters/{id}/progression/refund` | Body `{ purchase_id }` — devolve uma compra reembolsável |

Erros 400: compra inexistente, já devolvida, `refundable_xp == 0`, janela expirada (nova sessão iniciada).

### 3. Regras de reversão (WFRP)

- **Perícia:** decrementar `advances` em 1; remover entrada se `advances` chegar a 0
- **Talento:** remover da lista `talents`
- **Escopo MVP:** perícias e talentos já expostos em `/progression` (sem avanços de carreira — ainda não compráveis na UI)

### 4. Frontend (`/progression`)

- Seção **Compras desta sessão** listando entradas com `refundable_xp > 0` e botão **Devolver**
- Após devolução, atualizar XP disponível, contadores `atual +N` e lista de talentos
- Sem janela ativa → seção oculta

### 5. Spec deltas

- `character-management` — requisito de devolução limitada à última sessão
- `progression-ui` — UI de devolução
- `wfrp-rules-engine` — reversão mecânica e atribuição FIFO

---

## Out of Scope

- Devolver compras feitas com XP de sessões anteriores
- Devolver após iniciar nova sessão na mesma campanha
- Devolver avanços de carreira / atributo (não expostos na UI atual)
- Confirmação modal antes de comprar (só devolução)
- Histórico de devoluções além do ledger da janela corrente

---

## Acceptance Criteria

1. Sessão encerra com +50 XP → jogador compra Percepção +1 (5 XP) → **Devolver** restaura 5 XP e `atual +N` decrementa.
2. Com 50 XP de budget, três compras de 5 XP são reembolsáveis; compras adicionais só com XP antigo têm `refundable_xp = 0` e botão desabilitado.
3. Após **iniciar nova sessão**, compras da janela anterior não podem mais ser devolvidas.
4. Devolver talento remove-o da ficha e libera 10 XP (se atribuído ao budget).
5. `pytest` cobre compra → devolução → bloqueio pós-nova-sessão.
6. `openspec validate add-progression-refund-last-session --strict` passa.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| Personagens existentes sem campos novos | Defaults: `progression_refund_budget=0`, purchases=`[]` — sem devolução retroativa |
| Duplicatas legadas em `skills` | Reversão usa mesma lógica de `skill_advances_by_name` / update imutável |
| Jogador devolve e recompra em loop | Permitido dentro do budget; budget restaura em devolução |
