# Proposal: add-ambient-audio-engine

**Data:** 2026-06-23  
**Status:** Draft  
**Design:** `design.md`

---

## Why

A imersão narrativa do jogo não tem trilha sonora. Os arquivos de áudio já existem em `audio/` mas nunca foram integrados à aplicação. Adicionar música ambiente adaptativa aumenta significativamente o impacto emocional das cenas — especialmente nas transições entre exploração e tensão.

---

## Tracks disponíveis

| Arquivo | Categoria | Quando toca |
|---------|-----------|-------------|
| `Solo RPG Theme.mp3` | `menu` | Fora de sessão (login, campanhas, personagem) |
| `Solo RPG Theme 2.mp3` | `menu` | Fora de sessão (alternada com Theme) |
| `Solo RPG - Tension.mp3` | `tensão` | Cenas tensas durante sessão |
| `Solo RPG - Tension 2.mp3` | `tensão` | Cenas tensas durante sessão (alternada) |

Todos os tracks em **loop infinito** até serem trocados.

---

## Estados de áudio

| Estado | Trigger | Tracks |
|--------|---------|--------|
| `menu` | Qualquer página fora de `/play/...` | Theme (aleatório entre os 2) |
| `silencio` | Entrar em sessão OU fazer logout | Nenhum |
| `tensão` | LLM emite `[MUSICA]{"mood":"tensão"}` | Tension (aleatório entre os 2) |
| `normal` | LLM emite `[MUSICA]{"mood":"normal"}` | Nenhum (silêncio in-game) |

Transições: stop imediato do track atual → start do novo. Sem crossfade no MVP.

---

## What Changes

### 1. LLM — novo sinal `[MUSICA]`

Nova instrução no `gm-system-prompt.md`: o GM emite `[MUSICA]` ao início de cenas tensas e ao retorno à normalidade.

Payload:
```json
{"mood": "tensão" | "normal", "descricao": "breve contexto da cena"}
```

Critérios de cena tensa: fuga/perseguição, esconder-se de perigo, negociação de alta pressão, ambiente hostil (floresta à noite, esgotos, masmorras), confronto iminente, interrogatório.

### 2. Backend — parsing do sinal + campo na resposta

- `backend/app/llm/signals.py` (ou `gm_orchestrator.py`): ao encontrar sinal `MUSICA`, extrair `mood` e incluir em `TurnResult.scene_mood`
- `backend/app/services/gm_orchestrator.py`: `TurnResult` ganha campo `scene_mood: str | None = None`
- No payload SSE `done` de `stream_turn`: incluir campo `scene_mood`
- No retorno JSON de `process_turn`: incluir campo `scene_mood`

### 3. Frontend — `AudioManager` singleton + `useAudioPlayer`

- `frontend/src/lib/audio/audioManager.ts`: singleton module-level com métodos `play(category)` e `stop()`
- Seleciona track aleatório da categoria (ou alterna sequencialmente entre os dois)
- `frontend/src/hooks/useAudioPlayer.ts`: hook que expõe `setMood(mood)` e gerencia o ciclo de vida (stop on unmount)
- `frontend/src/app/providers.tsx` (ou layout): `AudioRoutingProvider` que observa mudança de rota:
  - Rota fora de `/play/...` → `play("menu")`
  - Rota `/play/...` → `stop()`
  - Logout → `stop()`
- `frontend/src/hooks/useSessionPlay.ts`: ao receber `scene_mood` no turn response → `setMood(scene_mood)`

### 4. Assets — Docker + build

- Mudar build context do `frontend` em `docker-compose.yml` de `./frontend` para `.` (project root) — mesmo padrão do backend
- Atualizar `frontend/Dockerfile` builder stage para `COPY audio ./public/audio/`
- Para dev local: adicionar script `prepare:audio` no `frontend/package.json` (`cp -r ../audio/*.mp3 public/audio/`)
- `.gitignore`: adicionar `frontend/public/audio/` (gerado via prepare:audio) e documentar o script

---

## Capabilities

### New Capabilities

- **audio-routing**: sistema frontend que gerencia qual categoria de áudio toca baseado na rota/estado
- **audio-mood-signal**: sinal `[MUSICA]` do LLM + processamento no backend + repasse ao frontend

---

## Impact

| Área | Alterações |
|------|------------|
| `Docs/gm-system-prompt.md` | Instrução de `[MUSICA]` signal (exemplos, critérios, formato) |
| `backend/app/services/gm_orchestrator.py` | `TurnResult.scene_mood`; handle sinal `MUSICA`; incluir em SSE done payload |
| `frontend/src/lib/audio/audioManager.ts` | Novo — singleton player |
| `frontend/src/hooks/useAudioPlayer.ts` | Novo — hook de controle de mood |
| `frontend/src/app/providers.tsx` | Routing-aware audio trigger |
| `frontend/src/hooks/useSessionPlay.ts` | Consume `scene_mood` do turn response |
| `frontend/package.json` | Script `prepare:audio` |
| `frontend/Dockerfile` | `COPY audio ./public/audio/` |
| `docker-compose.yml` | Build context frontend: `.` → `.` (project root) |

---

## Non-Goals

- Crossfade entre tracks no MVP
- Volume slider / controle de usuário (pode vir depois)
- Tracks de combate (não há arquivo de combate fornecido)
- Tracks de sessão encerrada
- Análise de sentimento no backend (sempre via sinal do LLM)
- Mobile audio restriction bypass (autoplay bloqueado em mobile sem interação — documentar limitação)

---

## Open Questions

| Questão | Decisão assumida |
|---------|-----------------|
| Autoplay sem interação do usuário? | Browsers modernos bloqueiam autoplay sem interação previa. O primeiro clique em "Iniciar Sessão" ou qualquer botão serve como interação suficiente para destravar o áudio. |
| O que toca entre cenas tensas (in-game, sem sinal `[MUSICA]`)? | Silêncio — o GM emite `[MUSICA]{"mood":"normal"}` para encerrar tensão |
| Tracks de sessão acabada (`FIM_SESSAO`)? | Fora de escopo — a rota muda e o theme toca normalmente |
