# Spec delta: session-ui

**Change:** `defer-gm-narrative-presentation`

---

## MODIFIED Requirements

### Requirement: Renderização Markdown no chat narrativo

Os blocos de narrativa do GM no `ChatLog` SHALL ser renderizados como Markdown, incluindo suporte a negrito, itálico, listas não-ordenadas e separadores horizontais. Linhas do jogador (`player-line`) e mensagens de sistema (`roll-system-msg`) NÃO devem receber renderização Markdown. **Texto bruto de sinais estruturados (`[TESTE]`, `[MUSICA]`, `[NOVA_CAMPANHA]`, etc.) MUST NOT aparecer no chat — nem durante SSE nem após `done`.**

#### Scenario: Negrito e itálico visíveis

- **WHEN** o GM emite uma narrativa contendo `**palavra**` ou `_palavra_`
- **THEN** o jogador vê "palavra" em negrito ou itálico, não o texto literal com asteriscos

#### Scenario: Texto do jogador sem Markdown

- **WHEN** o jogador digita uma ação com asteriscos, ex: `*atacar*`
- **THEN** o texto é exibido como digitado, sem renderização Markdown

#### Scenario: SSE em andamento não exibe tokens parciais

- **WHEN** tokens SSE chegam durante um turno do GM
- **THEN** o `ChatLog` SHALL NOT adicionar ou expandir entrada `narrative` com conteúdo parcial
- **AND** SHALL exibir indicador "Preparando a resposta…" até o evento `done`

#### Scenario: Narrativa revelada apenas após done

- **WHEN** o SSE emite `done` com `narrative` sanitizado
- **THEN** uma única entrada `narrative` é adicionada ao chat com o texto final
- **AND** o indicador "Preparando a resposta…" desaparece

---

### Requirement: Auto-scroll para nova mensagem

O chat de jogo SHALL rolar automaticamente para a mensagem mais recente toda vez que uma nova entrada for adicionada. **Durante preparação de resposta (sem entrada narrative parcial), scroll MUST NOT seguir tokens invisíveis.**

#### Scenario: Nova mensagem do GM

- **WHEN** o GM termina de narrar e uma nova `narrative-block` é adicionada no `done`
- **THEN** o chat rola suavemente até a última mensagem

#### Scenario: Preparação em andamento

- **WHEN** o turno está em andamento e apenas o indicador "Preparando a resposta…" está visível
- **THEN** o chat MAY manter scroll estável ou rolar suavemente até o indicador — MUST NOT criar flicker de texto bruto

#### Scenario: Histórico já carregado ao abrir sessão

- **WHEN** o jogador abre uma sessão com histórico existente
- **THEN** o scroll vai imediatamente (sem animação) para o fim do log antes de qualquer nova mensagem
