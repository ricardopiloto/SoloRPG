# Design: add-progression-refund-last-session

## Contexto

```
[FIM_SESSAO] → end_session()
                  ├─ xp_total += xp_awarded
                  └─ abre janela de progressão reembolsável
                         ↓
              /progression — compras (skill/talent)
                         ↓
              POST /progression/refund (opcional)
                         ↓
              start_session() → fecha janela (sem devolução)
```

Progressão permanece **100% server-side** (sem LLM), alinhada a `character-management` e `wfrp-rules-engine`.

---

## Modelo de dados

### Migration Alembic

Adicionar em `player_characters`:

```python
progression_source_session_id: UUID | None  # FK lógica → game_sessions.id
progression_refund_budget: int = 0          # XP restante atribuível da última sessão
progression_purchases: list = []            # JSON ledger
```

**Defaults para registros existentes:** budget `0`, purchases `[]`, session_id `null` → nenhuma devolução até próximo `end_session`.

### Formato `progression_purchases[]`

```json
{
  "id": "uuid",
  "type": "skill" | "talent",
  "skill_name": "Percepção",
  "linked_attribute": "I",
  "talent_name": null,
  "cost": 5,
  "refundable_xp": 5,
  "refunded": false,
  "created_at": "2026-06-26T12:00:00Z"
}
```

`refundable_xp` ∈ `[0, cost]`. Soma de `refundable_xp` das entradas não-refunded ≤ `xp_awarded` da sessão fonte.

---

## Atribuição FIFO do budget

Ao comprar com custo `C`:

```python
refundable = min(C, character.progression_refund_budget)
character.progression_refund_budget -= refundable
append_purchase(..., refundable_xp=refundable, cost=C)
character.xp_spent += C
```

**Exemplo:** última sessão +50 XP; jogador tinha 20 XP disponíveis antes (total 70 após sessão).

| Ordem | Compra | Custo | refundable_xp | budget restante |
|-------|--------|-------|---------------|-----------------|
| 1 | Percepção +1 | 5 | 5 | 45 |
| 2 | Robusto | 10 | 10 | 35 |
| … | … | … | … | … |
| 10 | (10ª compra 5 XP) | 5 | 5 | 0 |
| 11 | Percepção +1 | 5 | **0** | 0 |

A 11ª compra usa XP antigo — **não reembolsável**.

---

## Ciclo de vida da janela

| Evento | Ação |
|--------|------|
| `end_session(session)` | `progression_source_session_id = session.id`; `progression_refund_budget = session.xp_awarded`; `progression_purchases = []` |
| `purchase_*` | Append ledger + atribuição FIFO (só se `progression_source_session_id` set) |
| `refund_purchase(id)` | Reverte mecânica; `xp_spent -= cost`; `progression_refund_budget += refundable_xp`; `refunded = true` |
| `start_session(campaign)` | `progression_source_session_id = null`; `progression_refund_budget = 0`; purchases podem ser descartados ou mantidos arquivados — **nenhuma** entrada aceita refund |

**Sessão pausada retomada:** não reabre nem fecha janela — progressão ocorre entre sessões encerradas, não durante sessão ativa (já bloqueado implicitamente pelo fluxo UI recap → progression).

---

## Reversão mecânica

### `reverse_skill_advance(skills, skill_name) -> list`

Espelho imutável de `apply_skill_advance`:

- Encontra skill; se `advances <= 1`, remove entrada
- Senão decrementa `advances` em 1
- Se skill não existe → erro (compra inválida)

### `reverse_talent(talents, talent_name) -> list`

- Remove primeiro talento com `name == talent_name`
- Se não encontrado → erro

Ambas chamadas usam `flag_modified(char, "skills"|"talents")`.

---

## API e schemas

### `ProgressionOptionsOut` (extend)

```python
refund_budget_remaining: int = 0
refundable_purchases: list[ProgressionPurchaseOut] = []
progression_window_active: bool = False  # source_session_id != null
```

### `ProgressionRefundIn`

```python
purchase_id: UUID
```

### `refund_progression_purchase(db, character_id, purchase_id)`

Validações:

1. Personagem vivo e owned
2. `progression_source_session_id` não nulo
3. Purchase existe, `not refunded`, `refundable_xp > 0`
4. Aplica reversão + persist

---

## Frontend

### `/progression`

Nova seção acima ou abaixo das listas de compra:

```
Compras desta sessão (reembolsáveis)
┌─────────────────────────────────────────┐
│ Percepção +1 · 5 XP          [Devolver] │
│ Robusto · 10 XP              [Devolver] │
└─────────────────────────────────────────┘
XP reembolsável restante: 35 / 50
```

- Botão **Devolver** só se `refundable_xp > 0` e `!refunded`
- `loading` desabilita ações
- i18n PT-BR: `progression.refund`, `progression.refundSection`, etc.

### Fluxo pós-recap

Inalterado: `session/end` → link `/progression`. A janela já foi aberta em `end_session` antes do redirect.

---

## Arquivos tocados (implementação)

| Arquivo | Mudança |
|---------|---------|
| `backend/app/db/models.py` | Novos campos |
| `backend/alembic/versions/...` | Migration |
| `backend/app/services/session.py` | `end_session` abre janela; `start_session` fecha |
| `backend/app/services/character.py` | Ledger em purchase; `refund_progression_purchase`; extend `get_progression_options` |
| `backend/app/rules/careers.py` | `reverse_skill_advance`, `reverse_talent` |
| `backend/app/api/routes.py` | `POST .../progression/refund` |
| `backend/app/schemas/api.py` | DTOs |
| `backend/tests/test_api_integration.py` | Cenários refund |
| `frontend/src/app/progression/page.tsx` | UI devolução |
| `frontend/src/lib/api.ts` | `refundPurchase()` |
| `frontend/messages/pt-BR.json` | Strings |

---

## Decisões descartadas

| Alternativa | Motivo |
|-------------|--------|
| Devolver qualquer compra do histórico | Viola regra do usuário (só XP da última sessão) |
| Tabela relacional `progression_purchases` | JSON no personagem basta para MVP; poucas entradas por janela |
| Modal "confirmar compra" | Escopo pediu devolução, não prevenção |
| Pro-rata parcial por compra | `refundable_xp` já modela compras parcialmente reembolsáveis se custo > budget restante (edge: budget 3, compra 5 → refundable 3) |

**Nota edge case budget < cost:** se restam 3 XP no budget e jogador compra talento (10 XP), `refundable_xp = 3` — devolução restaura 10 XP ao pool (`xp_spent`) e +3 ao budget, revertendo talento inteiro.
