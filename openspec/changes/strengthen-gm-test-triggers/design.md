# Design: strengthen-gm-test-triggers

## Contexto

O fluxo de testes no prompt (`Docs/gm-system-prompt.md`) é completo em teoria — três tipos + critério geral — mas **falta uma lista negativa/positiva** de cenários onde o LLM tende a "narrar adiante". Percepção passiva (`gm-narrative`) cobre revelação de detalhes; esta change cobre **resolução contestada** (desfecho depende de perícia).

Implementação prevista: **somente prompt** (`Docs/gm-system-prompt.md`). O backend já carrega o arquivo via `prompts.py`; não há novo parser de sinal.

---

## Gatilhos obrigatórios (conceito)

```
┌─────────────────────────────────────────────────────────────┐
│  Jogador declara ação contestada OU narrativa impõe        │
│  (fuga, emboscada, combate)                                 │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
              ┌─────────────────────────┐
              │  Gatilho na checklist?   │
              └─────────────┬───────────┘
                    sim     │     não
                     ▼      │      ▼
              Emitir [TESTE]    Critério geral
              e PARAR           (incerteza + impacto)
                     │
                     ▼
              [RESULTADO DO SISTEMA]
                     │
                     ▼
              Narrar consequencia_*
```

### Perseguição (Atletismo)

**Errado (anti-padrão):**
> O homem começa a correr fugindo de você. Você dispara atrás dele e, após duas esquinas, o alcança pelo colarinho.

**Correto:**
1. Narrar o estímulo: homem corre.
2. Se jogador persegue (ou perseguição é inevitável): emitir `[TESTE]` Atletismo com modificador contextual (distância, terreno, carga).
3. Aguardar resultado; narrar alcançar **ou** perder com base em sucesso/falha.

- `obrigatorio: true` quando a fuga já aconteceu e seguir é a única resolução mecânica.
- `obrigatorio: false` + `opcao_alternativa` quando jogador pode desistir ("deixá-lo ir").

### Furtividade (Furtividade)

**Errado:**
> Você entra furtivamente pelo corredor lateral sem ser visto.

**Correto:**
1. Jogador declara infiltração → TIPO 1: apresentar risco + emitir `[TESTE]` Furtividade.
2. Aguardar; sucesso = passa despercebido; falha = guarda vira, cão late, etc.

Modificadores sugeridos no prompt: guardas alertas (-10), escuridão (+10), armadura ruidosa (-10).

### Combate — dual roll

**Errado:**
> O salteador desferre um golpe; você esquiva no último instante.

**Correto (sequência):**

| Passo | Quem | Sinal | Aguardar |
|-------|------|-------|----------|
| 1 | Atacante | `[TESTE]` `ataque_cc` ou `ataque_distancia` | Sim |
| 2 | Defensor (se acerto e pode reagir) | `[TESTE]` `teste_atributo` perícia `Esquivar` (Ag) ou parry Arma CC | Sim |
| 3 | — | Narrar desfecho com base nos dois resultados | — |

**Turno do jogador atacando:** passo 1 com `atacante: personagem`; passo 2 só se inimigo tem capacidade de esquiva/parry narrativa.

**Turno de inimigo atacando:** passo 1 com `atacante: <inimigo>`, `alvo: personagem`; passo 2 **obrigatório** — Esquivar do jogador antes de narrar ferimento.

Regra absoluta: **nunca** emitir `[ESTADO_COMBATE]` no mesmo turno sem ter completado os testes mecânicos da troca.

---

## Gap backend: dano antes da defesa

Hoje `execute_roll` com `ataque_cc` aplica wounds ao personagem **no acerto**, antes de um eventual segundo teste de Esquivar:

```python
# gm_orchestrator.py — wounds applied when attack.hit
if attack.hit and payload.get("alvo") == "personagem":
    wounds_after, at_zero = apply_wounds(...)
```

**Impacto:** GM pode emitir Esquivar após acerto, mas ferimento já foi aplicado mecanicamente.

**Decisão desta change (prompt-only):**

1. Instruir GM a emitir teste de **ataque primeiro**; só emitir Esquivar se `[RESULTADO]` indicar acerto.
2. Na narração pós-Esquivar bem-sucedido: descrever que o golpe não feriu (narrativa); ferimento mecânico já aplicado é inconsistência conhecida.
3. Registrar follow-up opcional `add-combat-defense-resolution` para adiar `apply_wounds` até após teste de defesa — **fora desta change**.

Alternativa MVP aceita pelo PO: priorizar **existência** dos testes (jogador rola dados) sobre paridade mecânica perfeita de defesa.

---

## Relação com tipos de teste existentes

| Cenário | Tipo no prompt | `obrigatorio` |
|---------|----------------|---------------|
| Perseguição após fuga | TIPO 2 | `true` |
| "Quero entrar furtivamente" | TIPO 1 | `false` (alternativa: desistir) |
| Combate ataque | TIPO 2 implícito | `true` |
| Combate defesa | TIPO 2 | `true` |
| Detalhe sensorial extra | TIPO 3 (passivo) | `false` — **não confundir** |

A nova seção MUST deixar claro: TIPO 3 **nunca** substitui teste contestado de Atletismo/Furtividade/combate.

---

## Validação

- **Manual:** três prompts de jogador (perseguição, furtividade, combate) com `LLM_PROVIDER=deepseek` — verificar `[TESTE]` emitido antes de desfecho.
- **Automatizado (leve):** nenhum teste de integração LLM obrigatório; opcional revisar fixtures mock existentes se houver cenários de combate.
