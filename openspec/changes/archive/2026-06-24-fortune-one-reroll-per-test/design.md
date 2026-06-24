# Design: fortune-one-reroll-per-test

## Context

Fluxo atual (`add-fate-fortune-mechanics`):

1. Jogador rola teste → `pending_roll_result` em `awaiting_narrate`
2. Se falhou e `fortune_current > 0` → UI oferece re-roll
3. Re-roll gasta 1 Fortuna e substitui resultado
4. Se falhou de novo e ainda há Fortuna → UI oferece **novamente** (bug de regra)

Regra alvo: **1 Fortuna = 1 re-roll por teste**, independente de quantas Fortunas restam na sessão.

## Goals / Non-Goals

**Goals:**

- Impedir segundo re-roll com Fortuna no mesmo teste GM.
- Manter Fortunas restantes para testes futuros na mesma sessão.
- Backend como fonte de verdade (UI não pode contornar).

**Non-Goals:**

- Limitar Fortuna por sessão além do pool existente.
- Re-roll parcial (só um dado de múltiplos) — um teste = uma rolagem d100.

## Decisions

### 1. Flag `fortune_reroll_used` em `pending_roll_result`

**Decisão:** JSON persistido na sessão:

```python
pending_roll_result = {
    ...
    "fortune_reroll_used": False,  # set True após execute_fortune_reroll
}
```

| Evento | `fortune_reroll_used` |
|--------|------------------------|
| Primeira rolagem (`execute_roll`) | `False` |
| Após `execute_fortune_reroll` | `True` |
| Novo `[TESTE]` do GM | reset (novo `pending_test`, sem `pending_roll_result`) |

**Alternativa rejeitada:** Contador no frontend — bypassável e perdido em refresh.

### 2. API `fortune_reroll_available`

**Decisão:** `RollResponse` inclui:

```python
fortune_reroll_available: bool  # failed && fortune_current > 0 && !fortune_reroll_used
```

Frontend usa esse campo em vez de inferir só por `fortune_current`.

### 3. Re-roll falho encerra opções

Após re-roll com Fortuna que ainda falha:

- UI mostra apenas "Continuar com falha" (sem botão Fortuna)
- Jogador pode narrar resultado final

Fortunas não gastas permanecem para o próximo teste.

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Jogador confunde "sem Fortuna" vs "já usou neste teste" | Mensagem clara no prompt; gemas Fortuna ainda visíveis |
| Estado stale após refresh | Flag no backend em `pending_roll_result` |

## Migration Plan

Deploy backend + frontend juntos. Sessões em `awaiting_narrate` sem a chave tratam `fortune_reroll_used` como `False` (compatível).

## Open Questions

Nenhuma.
