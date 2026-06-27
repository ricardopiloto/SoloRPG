# Proposal: add-gm-social-test-triggers

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `strengthen-gm-test-triggers`, `update-gm-prompt-perception`, `add-passive-discovery-tests`

---

## Why

`strengthen-gm-test-triggers` cobriu perseguição (Atletismo), furtividade e combate — mas interações **sociais contestadas** ainda são resolvidas na prosa sem rolagem. O jogador declara intenção de influenciar ou ler um NPC e o GM entrega informação ou confirma mentira sem `[TESTE]`.

Sintomas reportados:

1. **Extrair informações:** "Quero tentar extrair mais informações da dona da taverna" → deveria exigir **Charme** antes de revelar segredos.
2. **Detectar mentira:** "Percebo se ele está mentindo?" → deveria exigir **Intuição** antes de confirmar ou negar.

Gap adicional: **Intuição** aparece no prompt (`TIPO 3`, propostas de percepção passiva) mas **não existe** em `backend/app/rules/skills.py` (`SKILL_CATALOG`). Quick-roll e API de catálogo rejeitam a perícia; sidebar não a lista. Testes GM com `"pericia":"Intuição"` rolam com avanços 0 se o personagem não tiver a skill cadastrada — inconsistente com WFRP4e.

---

## What Changes

### 1. Catálogo de perícias — Intuição

- Adicionar `"Intuição": "I"` em `SKILL_CATALOG` (`backend/app/rules/skills.py`).
- Incluir em `PROGRESSION_SKILL_NAMES` (progressão entre sessões).
- Testes unitários cobrindo listagem e quick-roll.

### 2. Prompt GM — gatilhos sociais

Estender `GATILHOS OBRIGATÓRIOS DE TESTE` em `Docs/gm-system-prompt.md`:

| Gatilho | Perícia | Tipo |
|---------|---------|------|
| Persuadir, seduzir, extrair informação de NPC | Charme (Fel) | TIPO 1 |
| Jogador pergunta se NPC mente / lê intenções ocultas | Intuição (I) | TIPO 1 |
| Negociação com consequência (preço, favor, confissão) | Charme ou Intimidação | TIPO 1 |

Anti-padrões e exemplos JSON (taverna, mentira) conforme exemplos do jogador.

Atualizar exceção do critério geral: interações sociais **contestadas** (influência ou leitura de NPC) também exigem rolagem — conversa casual sem stakes continua isenta.

### 3. Distinção TIPO 1 vs TIPO 3 (Intuição)

- **TIPO 1 (contestado):** jogador pergunta explicitamente "ele está mentindo?" → `[TESTE]` Intuição, desfecho depende do resultado.
- **TIPO 3 (passivo):** GM já narrou estímulo social vago; Intuição revela camada extra (`obrigatorio: false`) — regra existente, não substituída.

### 4. Spec deltas

- `synthetic-gm`: ADD mandatory social test triggers.
- `gm-narrative`: ADD distinção social contestado vs passivo.
- `wfrp-rules-engine`: ADD Intuição ao catálogo MVP.

---

## Out of Scope

- Intimidação / Liderança como gatilhos obrigatórios completos (mencionados como orientação; exemplos focados em Charme + Intuição).
- Rebalanceamento de carreiras ou species skills para incluir Intuição em todas as fichas.
- Backend validar `pericia` do `[TESTE]` contra catálogo (melhoria futura).

---

## Acceptance Criteria

1. `Intuição` presente em `SKILL_CATALOG` com atributo `I`; API `/skills` e quick-roll aceitam a perícia.
2. Prompt contém gatilhos sociais com exemplos Charme (taverna) e Intuição (mentira).
3. Critério geral distingue conversa trivial vs influência/leitura contestada.
4. Specs atualizadas; `openspec validate add-gm-social-test-triggers --strict` passa.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| Excesso de testes em todo diálogo | Gatilho só quando jogador **tenta** influenciar ou **pergunta** sobre veracidade |
| Sobreposição com percepção passiva | Tabela TIPO 1 vs TIPO 3 no prompt e design.md |
| Personagens sem Intuição na ficha | Rolagem usa Fel/I base + 0 avanços — válido WFRP; progressão pode comprar depois |
