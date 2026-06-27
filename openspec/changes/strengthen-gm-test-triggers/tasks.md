# Tasks: strengthen-gm-test-triggers

## Fase 1 — Prompt: gatilhos obrigatórios

- [x] **T1** Adicionar seção `GATILHOS OBRIGATÓRIOS DE TESTE` em `Docs/gm-system-prompt.md` após `QUANDO EXIGIR TESTE`
- [x] **T2** Documentar gatilho **perseguição/fuga** → Atletismo (Ag), com anti-padrão e exemplo correto ("homem começa a correr…")
- [x] **T3** Documentar gatilho **infiltração/furtividade** → Furtividade (Ag), com anti-padrão ("quero entrar furtivamente…")
- [x] **T4** Listar modificadores contextuais sugeridos (terreno, escuridão, armadura, distância) para Atletismo e Furtividade
- [x] **T5** Ajustar critério geral: perseguição, furtividade e combate **nunca** são "sucesso narrativamente necessário"

## Fase 2 — Prompt: combate dual-roll

- [x] **T6** Reescrever bloco `MODO: COMBATE` com fluxo sequencial ataque → defesa → narração
- [x] **T7** Proibir explicitamente narrar acerto, esquiva, dano ou queda sem `[TESTE]` + `[RESULTADO DO SISTEMA]`
- [x] **T8** Adicionar exemplo de `[TESTE]` defensivo (`teste_atributo`, perícia `Esquivar`) após acerto de ataque inimigo
- [x] **T9** Reforçar regra de conduta #2 / item 10: combate **sempre** rola; `[ESTADO_COMBATE]` só após testes da troca
- [x] **T10** Nota no prompt sobre limitação conhecida (dano aplicado no acerto antes de Esquivar) — GM prioriza ordem correta dos sinais

## Fase 3 — Specs e docs

- [x] **T11** Spec deltas `synthetic-gm` e `gm-narrative` (cenários Given/When/Then)
- [x] **T12** Atualizar `CHANGELOG.md` (Unreleased) com entrada `strengthen-gm-test-triggers`
- [x] **T13** `openspec validate strengthen-gm-test-triggers --strict`

## Fase 4 — Validação manual

- [ ] **T14** Sessão mock/real: NPC foge → jogador persegue → `[TESTE]` Atletismo emitido antes de desfecho
- [ ] **T15** Jogador declara entrada furtiva → `[TESTE]` Furtividade antes de narrar sucesso/falha
- [ ] **T16** Combate: inimigo ataca → `[TESTE]` ataque + `[TESTE]` Esquivar antes de narrar ferimento

## Dependências

- T1–T5 independentes de T6–T10 (podem paralelizar)
- T11–T13 após T1–T10
- T14–T16 após merge do prompt

## Follow-up opcional (fora desta change)

- `add-combat-defense-resolution`: adiar `apply_wounds` até após teste de Esquivar/parry no backend
