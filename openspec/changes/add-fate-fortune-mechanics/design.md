# Design: add-fate-fortune-mechanics

## Context

Estado atual:
- `PlayerCharacter` tem `fate_*` e `fortune_*` independentes; pregens definem `fortune_max` manualmente (Helena: 3/2, Tobias: 2/1).
- `spend_fate_point()` sobrevive com 1 wound; `spend_fortune_point()` suporta `reroll` e `bonus_teste` (+10).
- `start_session()` não restaura Fortuna.
- UI (`CharacterSidebar`) mostra só Destino via `FateGems`.
- GM emite `[ACAO_SISTEMA]` tipos `usar_ponto_destino` e `usar_ponto_fortuna`.

Regras alvo (WFRP solo):

| Recurso | Uso | Recuperação |
|---------|-----|-------------|
| **Destino** | Evitar ferimento OU sobreviver golpe mortal | Nunca |
| **Fortuna** | Re-rolar teste falho | Início de cada sessão = `fate_current` |

## Goals / Non-Goals

**Goals:**

- Acoplar Fortuna ao Destino vigente no start de sessão.
- Destino: evitar wound increment ou anular mortalidade (1 wound).
- Fortuna: apenas re-roll de teste falho com dedução server-side.
- UI e GM alinhados às regras.

**Non-Goals:**

- Recuperar Destino entre sessões/campanhas.
- Fortuna persistir entre sessões (exceto dentro da mesma sessão ativa).
- Mecânicas de Insanity/Corruption.
- Comprar Destino/Fortuna com XP.

## Decisions

### 1. Fortuna derivada de `fate_current` (não `fate_max`)

**Decisão:** Ao `start_session()` de sessão **nova** (não retomada pausada), definir:

```python
fortune_current = fate_current
fortune_max = fate_current
```

**Rationale:** Jogador com 3 Destino inicia sessão com 3 Fortuna; se gastou 1 Destino na campanha, inicia com 2 Fortuna.

**Alternativa rejeitada:** Usar `fate_max` — ignoraria Destino já gasto permanentemente.

**Sessão pausada retomada:** manter `fortune_current`/`fortune_max` persistidos (Fortuna é recurso intra-sessão).

### 2. Destino — dois gatilhos de gasto

**Decisão:** `spend_fate_point()` aceita `reason: "avoid_wound" | "avoid_death"`:

| Motivo | Efeito |
|--------|--------|
| `avoid_wound` | Cancela incremento de wound pendente; wounds inalterados |
| `avoid_death` | Sobrevive golpe mortal com 1 wound (comportamento atual) |

GM emite `usar_ponto_destino` com `motivo` no payload.

### 3. Fortuna — somente re-roll

**Decisão:** Remover `bonus_teste` (+10). `spend_fortune_point()` só aceita `effect="reroll"`.

Fluxo de teste:
1. Jogador falha teste GM.
2. UI oferece "Gastar Ponto de Fortuna?" se `fortune_current > 0`.
3. POST re-roll → backend deduz Fortuna, executa nova rolagem.

**Alternativa rejeitada:** Manter +10 como opção — não está nas regras pedidas.

### 4. UI — duas fileiras de gemas

**Decisão:** `CharacterSidebar` exibe:

```
Destino  ◆◆◇
Fortuna  ◆◆◆
```

Reutilizar `FateGems` com label distinto ou extrair `ResourceGems` genérico.

### 5. Criação de personagem

**Decisão:** Remover input `fortune_max` da tela de criação. Na criação, setar `fortune_current = fate_max` e `fortune_max = fate_max` (primeira sessão ainda fará refresh, mas estado inicial coerente).

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Sessões existentes com `fortune_max` desalinhado | Refresh no próximo `start_session` corrige |
| GM emite Fortuna sem teste pendente | Backend rejeita gasto sem contexto válido |
| Jogador gasta Destino mid-session → Fortuna não muda até próxima sessão | Comportamento documentado — Fortuna amarrada ao start |

## Migration Plan

1. Deploy backend com refresh em `start_session` e regras atualizadas.
2. Deploy frontend com UI dual.
3. Atualizar GM prompt — sem migration de DB (campos já existem).

## Open Questions

- Confirmar se re-roll com Fortuna permite modificar resultado apenas uma vez por teste (assumido: sim, 1 Fortuna = 1 re-roll).
