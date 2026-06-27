# Proposal: defer-gm-narrative-presentation

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `add-game-chat-ux`, `signal-alignment`, `Docs/audio-engine.md`

---

## Why

Durante o SSE de turno, o frontend acumula tokens brutos da LLM e os renderiza em tempo real no `ChatLog`. O jogador vê trechos de sinais estruturados (`[MUSICA]`, `[TESTE]`, `[IMAGEM]`, `[NOVA_CAMPANHA]`, JSON de campanha, etc.) sendo “digitados” antes de virarem UI (teste, imagem, mood, persistência). Isso quebra a imersão — o chat parece um log técnico, não narrativa.

Além disso, sinais com **tag de fechamento inválida** (ex.: `[/NOVA_CAMAPANHA]` em vez de `[/NOVA_CAMPANHA]`) não são removidos por `parse_signals()` e aparecem no texto final exibido ao jogador, incluindo JSON interno de campanha que nunca deveria ser visível.

---

## Sintomas observados

1. **Streaming:** blocos `[MUSICA]`, `[TESTE]`, markdown parcial e JSON aparecem no chat enquanto a IA ainda responde.
2. **Pós-turno:** payload `[NOVA_CAMPANHA]` inteiro visível na narrativa quando a tag de fechamento está errada ou o parser não casa o bloco.
3. **UX atual:** existe “O Mestre narra…” abaixo do chat, mas o streaming **também** preenche o log — efeito duplicado e confuso.

---

## What Changes

### 1. Apresentação diferida (frontend)

- Enquanto o turno SSE não emitir `done`, o chat **não** adiciona entrada `narrative` com tokens parciais.
- Exibir indicador **“Preparando a resposta”** (i18n `session.preparingResponse`) no lugar do streaming narrativo.
- No evento `done`, inserir **uma única** entrada `narrative` com `result.narrative` já sanitizado pelo backend.
- Aplicar o mesmo fluxo em `runStreamTurn` e `streamRollNarrate` (`useSessionPlay.ts`).

### 2. Sanitização defensiva de sinais (backend)

- Reforçar `parse_signals()` / pós-processamento para remover blocos de sinal mesmo com fechamento tolerante (typos comuns em `NOVA_CAMPANHA`).
- Adicionar `strip_signal_artifacts(text)` como rede de segurança antes de persistir ou retornar `narrative`.
- Remover fallback `parsed.narrative or llm_text` que reintroduz texto bruto com sinais (`gm_orchestrator.py`).

### 3. Prompt GM (reforço)

- Lembrete explícito: tags de fechamento MUST coincidir com abertura (`[/NOVA_CAMPANHA]`, não variantes).
- Sinais nunca devem aparecer na prosa visível — apenas entre tags JSON.

### 4. Specs

- `session-ui`: substituir requisito de “streaming visível token a token” por “indicador de preparação + reveal único”.
- `synthetic-gm`: streaming SSE permanece (latência/conexão), mas texto bruto não é player-facing.
- `gm-narrative` (delta): narrativa player-visible MUST NOT conter blocos de sinal.

---

## Out of Scope

- Reescrever protocolo de sinais ou adicionar novos tags.
- Typewriter effect palavra a palavra após `done` (reveal instantâneo do bloco final).
- Ocultar entradas `player`, `roll`, `TestBlock`, `SceneImage` — só narrativa GM bruta/streaming.

---

## Acceptance Criteria

1. Durante turno em andamento, o jogador vê **“Preparando a resposta”** — nunca JSON de `[NOVA_CAMPANHA]` ou `[MUSICA]` parcial.
2. Após `done`, apenas a narrativa limpa aparece no chat (sem blocos de sinal).
3. Resposta com `[/NOVA_CAMAPANHA]` (typo) ainda remove o bloco do texto exibido; campanha persiste se JSON válido for extraído.
4. Testes backend cobrem strip tolerante; testes frontend cobrem ausência de entrada streaming no `entries`.
5. Histórico carregado de turnos anteriores continua exibindo narrativa já persistida (sanitizada).

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| Percepção de latência sem texto incremental | Indicador claro “Preparando a resposta”; SSE mantém conexão ativa |
| Strip agressivo remove prosa legítima | Patterns limitados a delimitadores de sinal conhecidos |
| Regressão auto-scroll | Scroll no `done` quando entrada final entra |
