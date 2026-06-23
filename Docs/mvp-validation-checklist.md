# Checklist — validação MVP (campanha 3–5 sessões)

Use este roteiro para validar o MVP com **DeepSeek real** (`LLM_PROVIDER=deepseek` + `DEEPSEEK_API_KEY` válida).  
Os testes automatizados (pytest + Playwright) usam `LLM_PROVIDER=mock` e não substituem esta validação.

## Pré-requisitos

- [ ] `./scripts/check-dev.sh` sem falhas críticas
- [ ] Backend: `DATABASE_URL` sqlite, `LLM_PROVIDER=deepseek`, chave configurada
- [ ] Frontend: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] **Conta autenticada** — login em `/login` (fase 1: senha `ADMIN_PASSWORD`; multi_user: register + verify)
- [ ] Personagem starter presente após login admin (ou após verify em multi_user)
- [ ] Tempo reservado: ~3–4 h (3–5 sessões de ~45 min cada, ou sessões encurtadas para teste)

## Sessão 1 — Abertura

- [ ] Selecionar personagem pré-gerado em `/character` (fase 1: wizard desligado)
- [ ] Iniciar campanha; primeira sessão gera `[NOVA_CAMPANHA]` (tom, local, NPCs)
- [ ] Narrativa coerente com WFRP; GM não quebra personagem (sem meta-comentário)
- [ ] Pelo menos um `[TESTE]` resolvido com rolagem server-side
- [ ] Timer visível; sessão pausável (botão ⏸ no header, retomada automática ao re-entrar)
- [ ] Encerramento com `[FIM_SESSAO]`: resumo legível + XP (30–100)

## Sessões 2–3 — Continuidade

- [ ] Retomar campanha ativa; contexto referencia eventos anteriores
- [ ] NPCs e facções mantêm consistência de nome e tom
- [ ] Diário atualizado (painel lateral) sem números de karma/reputação
- [ ] Combate ou exploração alternam sem travar o loop (se combate ocorrer)
- [ ] Imagens: placeholder ou Workers AI carrega sem quebrar o chat

## Sessões 4–5 (opcional) — Progressão e fechamento

- [ ] XP acumulado permite compra de perícia/talento em `/progression`
- [ ] Ficha reflete avanços após progressão
- [ ] Campanha pode ser marcada concluída em `/campaigns`
- [ ] Nenhuma contradição grave (nomes trocados, objetivos revelados, morte ignorada)

## Critérios de aceite

| Área | Aceite |
|------|--------|
| Auth | Dados isolados por conta; verify obrigatório em production |
| GM | Tom sombrio WFRP; rejeita input fora de personagem |
| Regras | Rolagens sempre server-side; `[TESTE]` antes do resultado |
| Memória | Resumos de sessão influenciam turnos seguintes |
| UI | Loop completo sem erro 500; recap e XP ao fim |
| Docs | README + [`phase1-release-runbook.md`](phase1-release-runbook.md) permitem setup |

## Registro de problemas

| Sessão | Problema | Severidade (baixa/média/alta) | Issue/nota |
|--------|----------|-------------------------------|--------------|
| | | | |

## Resultado

- [ ] **Aprovado** — pronto para uso pessoal / demo
- [ ] **Reprovado** — listar blockers acima e abrir change OpenSpec

Data: ___________  
Personagem / campanha testados: ___________
