# session-end-ux Specification

## Purpose
TBD - created by archiving change improve-session-end-flow. Update Purpose after archive.
## Requirements
### Requirement: Fim de sessão não redireciona automaticamente o jogador

Quando o backend sinaliza `session_ended: true`, o frontend SHALL exibir o encerramento dentro do chat e aguardar ação explícita do jogador antes de navegar. O frontend SHALL NOT redirecionar automaticamente para outra rota ao detectar `session_ended`.

#### Scenario: Última narrativa permanece visível após fim de sessão

- **Dado** que o GM emite `[FIM_SESSAO]` e o stream é concluído com `session_ended: true`
- **Quando** o evento `done` é processado pelo frontend
- **Então** a narrativa final SHALL estar visível no chat log
- **E** o frontend SHALL NOT redirecionar a página automaticamente
- **E** um banner de encerramento SHALL aparecer logo abaixo da narrativa final no chat

#### Scenario: sessionStorage ainda armazena recap ao fim de sessão

- **Dado** que `result.session_ended === true` e `result.player_summary` está disponível
- **Quando** o frontend processa o evento
- **Então** `sessionStorage["wfrp-recap"]` SHALL ser escrito com `{ summary, xp, campaignId, characterId }`
- **E** esse dado SHALL estar disponível quando o jogador navegar para `/session/end`

---

### Requirement: Banner inline de encerramento exibe opções de navegação

O `ChatLog` SHALL renderizar uma entrada do tipo `session-end` como um banner visual inline, integrado ao scroll do chat, com duas ações: continuar a campanha ou encerrar a sessão.

#### Scenario: Banner exibe XP ganho e duas ações

- **Dado** que uma entrada `{ kind: "session-end", xp: 75 }` existe no chat
- **Quando** o `ChatLog` renderiza essa entrada
- **Então** o banner SHALL exibir o XP ganho (ex: `+75 XP`)
- **E** SHALL exibir botão "Continuar campanha" que navega para `/campaigns`
- **E** SHALL exibir botão "Encerrar por hoje" que navega para `/session/end`
- **E** o banner SHALL ser estilizado de forma consistente com o tema WFRP (sem cores de alerta ou sucesso intrusivos)

#### Scenario: Banner rola com o chat sem bloquear conteúdo

- **Dado** que o banner `session-end` é renderizado no final do chat
- **Quando** o chat faz scroll automático para o fim
- **Então** o banner SHALL estar visível abaixo da narrativa final
- **E** o banner SHALL fazer parte do fluxo de scroll normal do `chat-log`
- **E** o banner SHALL NOT usar `position: fixed` ou `position: sticky`

---

### Requirement: Input de ação fica desabilitado após fim de sessão

Após uma entrada `session-end` ser adicionada ao chat, o campo de input e botão de envio SHALL ser desabilitados. O hint abaixo do input SHALL indicar que a sessão encerrou.

#### Scenario: Input desabilitado após session-end

- **Dado** que `sessionEnded === true` (derivado de `entries.some(e => e.kind === "session-end")`)
- **Quando** a área de input é renderizada
- **Então** o `<input name="action">` SHALL ter o atributo `disabled`
- **E** o `<button type="submit">` SHALL ter o atributo `disabled`
- **E** o hint SHALL exibir "Sessão encerrada." (não "Use ⏸ no topo para pausar.")

#### Scenario: Estados existentes de bloqueio não são afetados

- **Dado** que `sessionEnded === true` e `awaitingRoll === false`
- **Quando** a área de input é renderizada
- **Então** o input SHALL estar desabilitado apenas por `sessionEnded`
- **E** nenhum outro estado existente (`loading`, `awaitingRoll`, `diceRolling`) SHALL ser alterado

