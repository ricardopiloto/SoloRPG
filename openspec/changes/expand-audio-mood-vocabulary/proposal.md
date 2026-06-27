# Proposal: expand-audio-mood-vocabulary

**Data:** 2026-06-26  
**Status:** Draft  
**Design:** `design.md`  
**Relacionado:** `add-ambient-audio-engine`, `Docs/audio-engine.md`, `fix-audio-mute-routing-regression`

---

## Why

Hoje o GM só pode sinalizar `tensão` e `normal` via `[MUSICA]`. Os assets in-game já existem em `audio/` (Combat, Exploration, Investigation, Horror ×2, Social, Journey), mas o código reproduz apenas Tension. Ampliar o vocabulário de moods permite que a trilha acompanhe combate, exploração, investigação, horror sobrenatural vs. horror do Caos, social e jornada — sem alterar a arquitetura existente (singleton, sticky, mute, uma faixa por vez).

---

## Assets validados (`audio/`)

| Arquivo | Mood GM (`scene_mood`) | Categoria interna | Seleção |
|---------|------------------------|-------------------|---------|
| `Solo RPG Theme.mp3` | — (lobby) | `menu` | aleatória entre 2 Themes |
| `Solo RPG Theme 2.mp3` | — (lobby) | `menu` | aleatória entre 2 Themes |
| `Solo RPG - Tension.mp3` | `tensão` | `tensao` | aleatória entre 2 Tensions |
| `Solo RPG - Tension 2.mp3` | `tensão` | `tensao` | aleatória entre 2 Tensions |
| `SoloRPG - Combat.mp3` | `combate` | `combate` | aleatória entre 2 Combats |
| `SoloRPG - Combat 2.mp3` | `combate` | `combate` | aleatória entre 2 Combats |
| `SoloRPG - Exploration.mp3` | `exploração` | `exploracao` | aleatória entre 2 Explorations |
| `SoloRPG - Exploration 2.mp3` | `exploração` | `exploracao` | aleatória entre 2 Explorations |
| `SoloRPG - Investigation.mp3` | `investigação` | `investigacao` | aleatória entre 2 Investigations |
| `SoloRPG - Investigation 2.mp3` | `investigação` | `investigacao` | aleatória entre 2 Investigations |
| `SoloRPG - Horror.mp3` | `horror` | `horror` | aleatória entre 2 Horrors sobrenaturais |
| `SoloRPG - Horror 2.mp3` | `horror` | `horror` | aleatória entre 2 Horrors sobrenaturais |
| `SoloRPG - Horror Chaos.mp3` | `horror_caos` | `horror_caos` | aleatória entre 2 Horrors do Caos |
| `SoloRPG - Horror Chaos 2.mp3` | `horror_caos` | `horror_caos` | aleatória entre 2 Horrors do Caos |
| `SoloRPG - Social.mp3` | `social` | `social` | aleatória entre 2 Socials |
| `SoloRPG - Social 2.mp3` | `social` | `social` | aleatória entre 2 Socials |
| `SoloRPG - Journey.mp3` | `jornada` | `jornada` | aleatória entre 2 Journeys |
| `SoloRPG - Journey 2.mp3` | `jornada` | `jornada` | aleatória entre 2 Journeys |

**Nota de nomenclatura:** faixas legadas usam prefixo `Solo RPG` (com espaço); faixas novas usam `SoloRPG` (sem espaço). O `audioManager` MUST referenciar os nomes exatos dos arquivos; `encodeTrackPath` já trata espaços.

**Horror em dois moods distintos:** `horror` sorteia entre `Horror.mp3` / `Horror 2.mp3` (sobrenatural). `horror_caos` sorteia entre `Horror Chaos.mp3` / `Horror Chaos 2.mp3` (Caos/Ruína). Os pools **não** se misturam — o GM escolhe o mood; o sistema escolhe a variante dentro do pool.

---

## Moods in-game (payload `[MUSICA]`)

| `mood` | Quando o GM emite | Exemplos WFRP |
|--------|-------------------|---------------|
| `tensão` | Perigo iminente sem combate aberto | Perseguição, emboscada iminente, negociação sob pressão |
| `combate` | Combate mecânico em curso | Iniciativa, troca de golpes, fuga sob ataque |
| `exploração` | Ambiente hostil/desconhecido, sem perigo imediato | Ruína, masmorra, floresta — curiosidade + desconforto |
| `investigação` | Dedução, vigilância, interrogatório controlado | Seguir pistas, vigia discreta, analisar documentos |
| `horror` | Horror sobrenatural “clássico” | Mortos-vivos, espectros, ruínas assombradas, império antigo |
| `horror_caos` | Horror ligado ao Caos / Ruína | Warp, corrupção, mutação, rituais profanos, símbolos do Caos |
| `social` | Refúgio relativo, intrigas sem ameaça física imediata | Taverna calma, mercado, audiência |
| `jornada` | Deslocamento em viagem | Estrada, rio, carroça, acampamento em marcha |
| `normal` | Fim do tom emocional; silêncio in-game | Ameaça passou, refúgio seguro |

Regras herdadas de `audio-engine.md`:

- Silêncio in-game é o **default** até o primeiro `[MUSICA]`.
- Mood é **sticky** — turnos sem sinal mantêm a faixa atual.
- Emitir só na **transição** de tom, não a cada parágrafo.
- Volume ambiente baixo (6–9%); não competir com a narrativa.
- `normal` para qualquer trilha in-game; troca direta A→B permitida sem passar por `normal`.
- Mute global, `playGeneration`, idempotência por categoria e roteamento menu inalterados.

---

## What Changes

### 1. Frontend — `audioManager.ts`

- Estender `AudioCategory` com categorias in-game: `combate`, `exploracao`, `investigacao`, `horror`, `horror_caos`, `social`, `jornada` (além de `menu`, `tensao`).
- Preencher `TRACKS` e `VOLUME` com os MP3 validados acima.
- `horror` e `horror_caos`: **dois** MP3 cada (sorteio aleatório dentro do pool; pools separados)

### 2. Frontend — `useAudioPlayer.ts`

- Mapa `scene_mood` → `AudioCategory` (acentos no mood GM, slug sem acento na categoria).
- `setMood(mood)`: se `normal` → `stop()`; se mood conhecido e em `/play/` → `play(category)`; desconhecido → ignorar.

### 3. Backend — `gm_orchestrator.py`

- Whitelist de moods aceitos em `signal.tag == "MUSICA"` (inclui `horror_caos`).

### 4. Prompt GM — `Docs/gm-system-prompt.md`

- Expandir seção `[MUSICA]` com todos os moods, critérios e distinção `horror` vs `horror_caos`.
- Exemplos CORRETO/ERRADO para cada par de horror.

### 5. Documentação — `Docs/audio-engine.md`

- Atualizar tabelas de assets, moods e volumes; remover seção “evolução planejada” (passa a implementado).

### 6. Testes

- `audioManager.test.ts`: play por categoria, idempotência, troca entre moods, horror vs horror_caos usam arquivos distintos.
- Teste de mapeamento mood → categoria (unit ou no mesmo arquivo).

---

## Out of Scope

- Crossfade entre faixas.
- Moods `triunfo` / `luto` (sem assets).
- Análise automática de texto para mood (continua decisão do GM).
- Controle de volume pelo jogador (além de mute global).
- Novos arquivos MP3 além dos já presentes em `audio/`.

---

## Acceptance Criteria

1. GM emite `[MUSICA]{"mood":"combate",...}` em sessão → trilha Combat toca em loop (~9% volume).
2. GM emite `horror` → sorteia entre `SoloRPG - Horror.mp3` / `Horror 2.mp3`; `horror_caos` → sorteia entre `Horror Chaos.mp3` / `Horror Chaos 2.mp3`.
3. `normal` para qualquer trilha in-game ativa.
4. Mute, sticky, menu lobby, uma faixa audível, `playGeneration` — comportamento idêntico ao atual.
5. Moods inválidos ignorados no backend e frontend sem erro visível.
6. `npm run test:unit` passa com novos casos.

---

## Risks

| Risco | Mitigação |
|-------|-----------|
| GM confunde `horror` e `horror_caos` | Critérios explícitos no prompt + exemplos WFRP |
| GM emite mood em todo turno | Reforçar regra “só na transição” |
| Nomes de arquivo com espaço vs sem espaço | Paths literais no `TRACKS`; teste de encode |
