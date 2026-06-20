# Proposal: sync-gm-prompt-v23

**Data:** 2026-06-16  
**Status:** Draft  
**Escopo:** `backend/app/services/campaign.py` + `backend/app/services/gm_orchestrator.py` + `frontend/src/components/session/TestBlock.tsx`

---

## Contexto

O `Docs/gm-system-prompt.md` foi atualizado para a **versão 2.4** (anterior: 2.3), introduzindo:

- **Dois tipos de teste** com campo `"obrigatorio": true/false` e `"opcao_alternativa"` no `[TESTE]`
- **Clarificação semântica de `obrigatorio` (v2.4):** "A obrigatoriedade é do teste, não da rolagem." — em testes obrigatórios (`obrigatorio: true`), o jogador *não pode pular*, mas **sempre clica em rolar**. A diferença é narrativo-UX, não mecânica. O componente de dado é sempre exibido.
- **Novo formato de `[NOVA_CAMPANHA]`** com `"ponto_de_partida"` (renomeado de `"gancho_inicial"`), `"ganchos_ocultos"` e campo `"voz"` nos NPCs
- **Novo formato de `[ESTADO_COMBATE]`** com `"inimigos[].status"` e `"proxima_acao"` em cada turno de combate

O backend carrega o prompt diretamente de `gm-system-prompt.md` (via `load_gm_system_prompt()`), então as instruções ao LLM já estão atualizadas. Mas o código que **interpreta os sinais retornados** pelo LLM ainda usa o formato antigo — causando dados perdidos.

---

## Bugs identificados

### Bug 1 — `apply_nova_campanha`: campo `ponto_de_partida` não lido

```python
# campaign.py:52 — lê o nome de campo ANTIGO
campaign.world_state = payload.get("gancho_inicial")
```

O prompt v2.3 envia `"ponto_de_partida"`, não `"gancho_inicial"`. Como resultado, a situação de abertura da campanha nunca é gravada em `campaign.world_state`. O contexto injetado ao GM em sessões subsequentes sempre mostrará `<estado_do_mundo>` vazio.

### Bug 2 — `apply_nova_campanha`: `ganchos_ocultos` ignorado

O prompt v2.3 envia `"ganchos_ocultos": ["...", "...", "..."]` no `[NOVA_CAMPANHA]`, mas `apply_nova_campanha` não lê esse campo. Os três ganchos secretos que conectam a abertura ao objetivo da campanha são descartados — sem registro no banco, o GM não pode referenciá-los em sessões futuras.

### Bug 3 — `_handle_combat_state`: `inimigos[].status` e `proxima_acao` ignorados

O prompt v2.3 emite ao final de cada turno:

```json
[ESTADO_COMBATE]
{
  "turno": 3,
  "personagem": { "wounds": "8/12", "fortune": 2 },
  "inimigos": [{ "nome": "Salteador", "status": "ferido" }],
  "proxima_acao": "personagem"
}
```

O handler `_handle_combat_state` (else branch) apenas atualiza `combat_state["turn"]` a partir de `payload.get("turno")`, mas ignora `inimigos` e `proxima_acao`. O estado de combate persistido nunca reflete o status dos inimigos (ferido/morto/fugiu) nem de quem é a próxima ação.

### Bug 4 — Frontend `TestBlock`: `opcao_alternativa` não exibida e distinção `obrigatorio` ausente

O payload do `[TESTE]` inclui `"opcao_alternativa": "Recuar pelo beco"` para testes opcionais, mas o `TestBlock.tsx` não renderiza esse campo. O jogador não vê a alternativa disponível sem ter que reler o texto narrativo.

Adicionalmente, o v2.4 clarifica que `obrigatorio: true` significa que o jogador *não pode pular o teste*, mas **sempre rola o dado** (analogia: numa mesa física, o GM pede o teste e o jogador pega o dado). O `TestBlock` deve:
- Para `obrigatorio: true`: mostrar título "Teste obrigatório", **sem** exibir alternativa, botão de rolar sempre visível
- Para `obrigatorio: false` (ou ausente): mostrar título "Teste solicitado", exibir `opcao_alternativa` se presente, botão de rolar visível

**O botão de rolar é sempre exibido** — em ambos os casos o jogador controla a rolagem.

---

## Solução proposta

### 1. `apply_nova_campanha` — corrigir campo renomeado + persistir `ganchos_ocultos`

```python
# Ler novo nome com fallback para compatibilidade
campaign.world_state = payload.get("ponto_de_partida") or payload.get("gancho_inicial")

# Gravar ganchos ocultos na campaign_summary
hooks = payload.get("ganchos_ocultos", [])
if hooks:
    campaign.campaign_summary = "[GANCHOS OCULTOS]\n" + "\n".join(f"- {h}" for h in hooks)
```

### 2. `_handle_combat_state` — armazenar status de inimigos e próxima ação

No else branch, ao receber o formato de turno do prompt v2.3:

```python
inimigos = payload.get("inimigos")
if inimigos is not None:
    state = dict(session.combat_state or {})
    for enemy_update in inimigos:
        nome = enemy_update.get("nome")
        status = enemy_update.get("status")
        for combatant in state.get("combatants", []):
            if combatant.get("nome") == nome:
                combatant["status"] = status
    session.combat_state = state

proxima_acao = payload.get("proxima_acao")
if proxima_acao is not None:
    state = dict(session.combat_state or {})
    state["proxima_acao"] = proxima_acao
    session.combat_state = state
```

### 3. `TestBlock.tsx` — exibir `opcao_alternativa` e diferenciar testes obrigatórios (v2.4)

**O botão "Rolar dado" é sempre exibido** — o jogador sempre controla a rolagem (v2.4: "a obrigatoriedade é do teste, não da rolagem").

- Quando `p.obrigatorio === true`: título "Teste obrigatório", sem bloco de alternativa
- Quando `p.obrigatorio` for `false` ou ausente: título "Teste solicitado"; se `p.opcao_alternativa` existir, exibir texto da alternativa abaixo do botão

---

## Não-escopo

- **`voz` do NPC**: o modelo `NPC` não tem coluna `voice`; adicionar essa coluna requer migração e está fora do escopo desta change. O campo `voz` é informacional e não afeta mecânicas.
- **`bs_base` e `forca_base`**: o backend já ignora corretamente esses valores do LLM e usa os atributos reais do personagem do banco. Nenhuma mudança necessária.
- **`karma_delta` / `reputacao_delta` em `[FIM_SESSAO]`**: já tratados corretamente em `persist_session_summary` (linhas 286-313 de `memory.py`). ✓
- **`percepcao_social` no contexto**: já injetado em `build_context_xml` (linha 52 de `memory.py`). ✓
