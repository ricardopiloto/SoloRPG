# Spec delta: chat-ux

**Change:** `defer-gm-narrative-presentation`

---

## ADDED Requirements

### Requirement: Chat SHALL show preparing indicator during GM turn

Enquanto um turno GM está em processamento (SSE aberto, aguardando `done`), a coluna de chat SHALL exibir mensagem **"Preparando a resposta…"** em estilo sutil (`text-wfrp-muted`, pulse opcional). O indicador MUST NOT ser confundido com entrada narrativa do Mestre.

#### Scenario: Indicador visível após envio do jogador

- **Dado** que o jogador enviou uma ação e `loading=true`
- **Quando** tokens SSE ainda não completaram o turno
- **Então** "Preparando a resposta…" SHALL estar visível na área de chat
- **E** nenhum bloco `chat-attribution` "Mestre" SHALL aparecer até a narrativa final

#### Scenario: Indicador oculto após done

- **Dado** que o SSE retornou `done` com narrativa
- **Quando** a entrada `narrative` é renderizada
- **Então** o indicador "Preparando a resposta…" SHALL desaparecer

#### Scenario: Indicador durante narração pós-rolagem

- **Dado** que o jogador clicou em "Rolar dado" e `streamRollNarrate` está ativo
- **WHEN** aguardando `done`
- **THEN** o mesmo indicador "Preparando a resposta…" SHALL ser exibido
- **AND** tokens parciais SHALL NOT aparecer no log
