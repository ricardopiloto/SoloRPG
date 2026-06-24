# Tasks: sync-gm-prompt-v23 (atualizado para v2.4)

## 1. Backend — `campaign.py` (`apply_nova_campanha`)

- [x] 1.1 Substituir `payload.get("gancho_inicial")` por `payload.get("ponto_de_partida") or payload.get("gancho_inicial")` para compatibilidade com v2.3 e retrocompatibilidade
- [x] 1.2 Após criar NPCs, ler `payload.get("ganchos_ocultos", [])` e, se não vazio, gravar em `campaign.campaign_summary` como bloco `"[GANCHOS OCULTOS]\n- hook1\n- hook2\n- hook3"`

## 2. Backend — `gm_orchestrator.py` (`_handle_combat_state`)

- [x] 2.1 No else branch (formato turno v2.3), após atualizar `state["turn"]`, ler `payload.get("inimigos")` e, se presente, iterar sobre a lista atualizando `combatant["status"]` nos combatentes com o mesmo `nome` em `state.get("combatants", [])`
- [x] 2.2 Ler `payload.get("proxima_acao")` e, se presente, gravar em `state["proxima_acao"]`
- [x] 2.3 Garantir que `session.combat_state` seja reatribuído após as mutações (SQLAlchemy requer reatribuição para detectar mudança em JSON)

## 3. Frontend — `TestBlock.tsx`

> **v2.4:** "A obrigatoriedade é do teste, não da rolagem" — o botão "Rolar dado" é sempre exibido independentemente de `obrigatorio`. A diferença é apenas de título e de exibição da alternativa.

- [x] 3.1 Exibir título dinâmico: `p.obrigatorio === true` → "Teste obrigatório"; caso contrário → "Teste solicitado"
- [x] 3.2 Quando `p.opcao_alternativa` existir **e** `p.obrigatorio !== true`: renderizar bloco abaixo do botão de rolar com label "Ou:" e o texto da alternativa — em estilo `text-wfrp-muted text-sm italic`
- [x] 3.3 Garantir que o botão "Rolar dado" esteja sempre visível e habilitado — não remover nem desabilitar para testes obrigatórios
- [x] 3.4 Confirmar que o tipo `PendingTest.payload` em `@/lib/api` inclui `obrigatorio?: boolean` e `opcao_alternativa?: string | null`; adicionar se ausente

## 4. Validação

- [ ] 4.1 `npm run build` sem erros de TypeScript ✓
- [ ] 4.2 `ruff check backend/` sem erros ✓
- [ ] 4.3 Teste manual: criar nova campanha em sessão 1, verificar que `campaign.world_state` recebe `ponto_de_partida` e `campaign.campaign_summary` recebe os `ganchos_ocultos`
- [ ] 4.4 Teste manual: em combate, verificar que após [ESTADO_COMBATE] o `combat_state` contém `inimigos[].status` e `proxima_acao`
- [ ] 4.5 Teste manual: forçar [TESTE] com `obrigatorio: false` e `opcao_alternativa` preenchido — verificar que `TestBlock` exibe o texto da alternativa abaixo do botão de rolar
- [ ] 4.6 Teste manual: forçar [TESTE] com `obrigatorio: true` — verificar que título mostra "Teste obrigatório", alternativa não aparece, e botão de rolar está disponível normalmente
