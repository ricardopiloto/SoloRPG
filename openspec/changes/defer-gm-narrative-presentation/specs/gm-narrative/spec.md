# Spec delta: gm-narrative

**Change:** `defer-gm-narrative-presentation`

---

## ADDED Requirements

### Requirement: Player-visible narrative MUST NOT contain signal blocks

O texto exibido ao jogador no chat (`TurnResult.narrative`, histórico persistido, SSE `done.narrative`) SHALL NOT conter blocos de sinal estruturado — nem tags abertas/fechadas, nem JSON de payload de `[NOVA_CAMPANHA]`, `[MUSICA]`, `[TESTE]`, `[IMAGEM]`, `[FIM_SESSAO]`, `[ESTADO_COMBATE]`, `[ACAO_SISTEMA]`.

#### Scenario: NOVA_CAMPANHA com tag de fechamento typo

- **Dado** que a resposta LLM contém `[NOVA_CAMPANHA]{...}[/NOVA_CAMAPANHA]` (typo no fechamento)
- **Quando** o backend processa o turno
- **Então** o payload de campanha MAY ser extraído e persistido
- **E** `narrative` retornado ao frontend SHALL NOT conter o bloco JSON nem as tags

#### Scenario: MUSICA removida da prosa

- **Dado** que a resposta contém `[MUSICA]{"mood":"tensão",...}[/MUSICA]` seguido de narração
- **Quando** o turno completa
- **Então** o jogador vê apenas a narração em PT-BR
- **E** `scene_mood` é aplicado via metadado do turno, não via texto visível

#### Scenario: Falha de parse não reexpõe llm_text bruto

- **Dado** que `parse_signals` não extraiu algum bloco
- **Quando** o orchestrator monta `result.narrative`
- **Então** SHALL aplicar `strip_signal_artifacts()` antes de persistir/retornar
- **E** SHALL NOT usar fallback `parsed.narrative or llm_text` que reintroduz sinais

#### Scenario: Diálogo com colchetes preservado

- **Dado** que a narrativa contém fala do NPC com texto normal sem tags de sinal
- **Quando** sanitização roda
- **Então** o diálogo permanece intacto no chat
