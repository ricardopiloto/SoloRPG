# Design: add-gm-social-test-triggers

## Contexto

Complementa `strengthen-gm-test-triggers` (físico/combate) com **interações sociais contestadas**. Charme já existe no catálogo; Intuição é referenciada no prompt mas ausente do código.

---

## Intuição no catálogo MVP

WFRP4e: Intuição (Intuition) usa atributo **Iniciativa (I)** — mesmo vínculo de Percepção, Orientação e Navegação.

```python
# skills.py — adição proposta
"Intuição": "I",
```

Impacto:

| Superfície | Comportamento após change |
|------------|---------------------------|
| `GET /api/skills` | Lista Intuição com `linked_attribute: I` |
| Quick-roll sidebar | Permite rolar Intuição |
| `[TESTE]` GM com `"pericia":"Intuição"` | Resolve com `I` + avanços do personagem |
| Progressão entre sessões | Intuição disponível para compra (PROGRESSION_SKILL_NAMES) |

Não migrar fichas existentes automaticamente — personagem sem avanços rola `I` puro (comportamento atual para perícias não possuídas).

---

## Gatilhos sociais (conceito)

```
Jogador declara influência ou leitura social
              │
              ▼
    ┌─────────────────────┐
    │ Stakes + incerteza? │
    └─────────┬───────────┘
         sim  │  não (papinho)
              ▼              ▼
        Emitir [TESTE]   Narrar livre
        Charme ou
        Intuição
              │
              ▼
    [RESULTADO DO SISTEMA]
              │
              ▼
    Narrar consequencia_*
```

### Charme — extrair informação

**Errado:**
> Você sorri para a dona da taverna e ela confidencia que o mercador sumiu há três noites.

**Correto:**
1. Jogador: "Quero tentar extrair mais informações da dona da taverna."
2. GM apresenta tom da conversa + risco (ela está fechada, clientes ouvem).
3. `[TESTE]` Charme → aguardar.
4. Sucesso: revela informação útil; falha: evasiva ou hostilidade.

Modificadores sugeridos: NPC já favorável (+10), ambiente público (-10), personagem visivelmente armado (-10), gorjeta recente (+10).

### Intuição — detectar mentira (pedido explícito)

**Errado:**
> Você olha nos olhos dele e percebe claramente que está mentindo.

**Correto:**
1. Jogador: "Percebo se ele está mentindo?"
2. `[TESTE]` Intuição (`obrigatorio: false` ou `true` conforme stakes) → aguardar.
3. Sucesso: indícios concretos (evita contato visual, hesita); falha: incerteza — "não consegue ler".

Modificadores: mentiroso experiente (-10), personagem já desconfia (+10), NPC sob stress (+10).

---

## TIPO 1 vs TIPO 3 — Intuição

| Situação | Tipo | `obrigatorio` | Quem inicia |
|----------|------|---------------|-------------|
| "Ele está mentindo?" (jogador pergunta) | TIPO 1 contestado | `false` + alternativa desistir | Jogador |
| GM narrou fala evasiva; camada extra possível | TIPO 3 passivo | `false` | GM |
| NPC mentindo; jogador não perguntou | TIPO 3 / percepção passiva | `false` | GM (`update-gm-prompt-perception`) |

Regra: TIPO 3 **nunca** responde "sim, ele mente" como desfecho único quando o jogador **pediu** resolução — use TIPO 1 com consequências explícitas.

---

## Relação com gatilhos existentes

Estender tabela em `GATILHOS OBRIGATÓRIOS`:

| Gatilho | Perícia | Tipo |
|---------|---------|------|
| … (Atletismo, Furtividade, combate — já existentes) | | |
| Persuadir / extrair informação | Charme | TIPO 1 |
| Ler veracidade ou intenção oculta (pedido explícito) | Intuição | TIPO 1 |

Atualizar linha de exceção do critério geral:

> perseguição, furtividade, combate **e interações sociais contestadas** sempre exigem rolagem

Conversa casual ("pergunto o caminho da taverna") permanece isenta.

---

## Validação

- **Automatizado:** teste que `list_skills()` inclui Intuição; quick-roll com `skill=Intuição` não levanta erro.
- **Manual:** taverna + Charme; "está mentindo?" + Intuição; verificar `[TESTE]` antes do desfecho.
