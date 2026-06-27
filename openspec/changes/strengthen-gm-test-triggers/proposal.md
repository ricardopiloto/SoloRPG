# Proposal: strengthen-gm-test-triggers

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `update-gm-prompt-perception`, `add-passive-discovery-tests`, `Docs/gm-system-prompt.md`

---

## Why

O prompt do GM já descreve três tipos de teste (escolha do jogador, exigido pela situação, passivo de descoberta) e um critério geral de incerteza — mas na prática o LLM **pula testes** em situações onde o desfecho depende claramente de perícia/atributo. O jogador vê a narrativa resolver a cena sem rolagem, quebrando a expectativa WFRP4e de mesa física.

Sintomas reportados:

1. **Perseguição:** GM narra "o homem começa a correr" e o jogador persegue sem `[TESTE]` de Atletismo — o desfecho (alcançar ou perder) fica arbitrário na prosa.
2. **Furtividade declarada:** Jogador diz "quero entrar furtivamente" e o GM descreve sucesso/falha sem `[TESTE]` de Furtividade.
3. **Combate:** GM narra acertos, esquivas e ferimentos **sem emitir `[TESTE]`** para atacante e defensor — violando regra de conduta #2 e o protocolo de combate.

Testes passivos de descoberta (`gm-narrative`) cobrem Percepção/Intuição em estímulos ambientais; **não** cobrem ações contestadas (correr atrás de alguém, infiltrar-se, trocar golpes).

---

## What Changes

### 1. Nova seção no prompt: **GATILHOS OBRIGATÓRIOS DE TESTE**

Adicionar checklist explícita em `Docs/gm-system-prompt.md` (após `QUANDO EXIGIR TESTE`) com cenários que **SEMPRE** exigem `[TESTE]` antes de resolver o desfecho:

| Gatilho | Perícia/atributo | Tipo |
|---------|------------------|------|
| Perseguir ou acompanhar alguém em fuga (corrida, escalada rápida) | Atletismo (Ag) | TIPO 1 ou 2 conforme quem iniciou |
| Infiltração, esconder-se, mover-se sem ser visto/ouvido | Furtividade (Ag) | TIPO 1 quando jogador declara; TIPO 2 se situação impõe |
| Qualquer ação de combate (ataque, defesa reativa, fuga sob fogo) | WS/BS + Esquivar ou Arma CC | Sempre `[TESTE]` — nunca narrar hit/miss sem rolagem |
| NPC ataca o personagem | Ataque inimigo + defesa do jogador | Dois testes sequenciais (ver design.md) |

Incluir os exemplos do jogador como blocos few-shot no prompt.

### 2. Reforço da seção **MODO: COMBATE**

- Proibir narrar golpe, esquiva, dano ou queda **antes** de `[TESTE]` + `[RESULTADO DO SISTEMA]`.
- Fluxo obrigatório por troca: (1) teste de ataque (`ataque_cc` / `ataque_distancia`); (2) se acerto e o alvo pode reagir, teste de defesa (`teste_atributo` com `Esquivar` ou parry via Arma CC); (3) só então narrar consequência.
- Regra de conduta absoluta reforçada: combate **nunca** resolve mecânica só na prosa.

### 3. Ajuste do critério geral

Clarificar que "sucesso narrativamente necessário para avançar" **não** se aplica a perseguição, furtividade ou combate — nesses casos a incerteza é estrutural.

### 4. Spec deltas

- `synthetic-gm`: MODIFIED `Combat Narration Protocol`; ADDED `Mandatory situational test triggers`.
- `gm-narrative`: ADDED distinção entre teste passivo (profundidade) e teste contestado obrigatório (desfecho).

---

## Out of Scope

- Novo `tipo` de sinal backend para defesa (`defesa_cc`) — documentado como follow-up opcional em `design.md`.
- Reescrever motor de combate (dano, DR, críticos) — permanece em `wfrp-rules-engine`.
- Testes automáticos com LLM real (DeepSeek) — validação manual + mock onde existir.

---

## Acceptance Criteria

1. Prompt contém seção **GATILHOS OBRIGATÓRIOS** com Atletismo (perseguição), Furtividade (infiltração) e combate dual-roll.
2. Exemplos literais do jogador aparecem no prompt como anti-padrão → padrão correto.
3. Regra de combate proíbe narrar acerto/ferimento sem `[TESTE]` prévio.
4. Specs `synthetic-gm` e `gm-narrative` atualizadas com cenários Given/When/Then.
5. `openspec validate strengthen-gm-test-triggers --strict` passa.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| GM emite dois testes por turno de combate (latência) | Fluxo sequencial explícito; aceitável para fidelidade WFRP |
| Backend aplica dano no acerto antes de teste de Esquivar | Documentar gap; prompt orienta ordem; follow-up backend opcional |
| Excesso de testes em ações triviais | Checklist limitada a gatilhos claros; critério geral de trivialidade mantido |
