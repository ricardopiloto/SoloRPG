# Design: expand-audio-mood-vocabulary

## Contexto

O motor de áudio atual (`Docs/audio-engine.md`) já define:

- Singleton `audioManager` com `playGeneration`, mute, idempotência por `currentCategory`.
- Lobby controlado por `AudioRoutingProvider`; in-game por `scene_mood` do turno.
- Apenas `tensão` / `normal` implementados no código, embora 14 MP3 in-game existam em `audio/`.

Esta change **estende** o vocabulário sem nova arquitetura.

---

## Fluxo de dados (inalterado)

```
[MUSICA]{"mood":"combate","descricao":"..."}
  → gm_orchestrator: scene_mood = "combate"
  → SSE done / TurnResponse
  → useSessionPlay.applyMeta → setMood("combate")
  → useAudioPlayer: MOOD_TO_CATEGORY["combate"] = "combate"
  → audioManager.play("combate")
```

`descricao` continua informativa (logs futuros, orientação do GM); frontend ignora.

---

## Mapa mood → categoria → arquivos

```typescript
// Valores expostos ao GM (scene_mood / JSON mood) — PT com acento onde aplicável
type SceneMood =
  | "tensão"
  | "combate"
  | "exploração"
  | "investigação"
  | "horror"
  | "horror_caos"
  | "social"
  | "jornada"
  | "normal";

// Categoria interna audioManager (slug ASCII)
type InGameCategory =
  | "tensao"
  | "combate"
  | "exploracao"
  | "investigacao"
  | "horror"
  | "horror_caos"
  | "social"
  | "jornada";

const MOOD_TO_CATEGORY: Record<string, InGameCategory> = {
  "tensão": "tensao",
  "combate": "combate",
  "exploração": "exploracao",
  "investigação": "investigacao",
  "horror": "horror",
  "horror_caos": "horror_caos",
  "social": "social",
  "jornada": "jornada",
};
```

### TRACKS (paths exatos validados em `audio/`)

```typescript
const TRACKS = {
  menu: [
    "/audio/Solo RPG Theme.mp3",
    "/audio/Solo RPG Theme 2.mp3",
  ],
  tensao: [
    "/audio/Solo RPG - Tension.mp3",
    "/audio/Solo RPG - Tension 2.mp3",
  ],
  combate: [
    "/audio/SoloRPG - Combat.mp3",
    "/audio/SoloRPG - Combat 2.mp3",
  ],
  exploracao: [
    "/audio/SoloRPG - Exploration.mp3",
    "/audio/SoloRPG - Exploration 2.mp3",
  ],
  investigacao: [
    "/audio/SoloRPG - Investigation.mp3",
    "/audio/SoloRPG - Investigation 2.mp3",
  ],
  horror: [
    "/audio/SoloRPG - Horror.mp3",
    "/audio/SoloRPG - Horror 2.mp3",
  ],
  horror_caos: [
    "/audio/SoloRPG - Horror Chaos.mp3",
    "/audio/SoloRPG - Horror Chaos 2.mp3",
  ],
  social: [
    "/audio/SoloRPG - Social.mp3",
    "/audio/SoloRPG - Social 2.mp3",
  ],
  jornada: [
    "/audio/SoloRPG - Journey.mp3",
    "/audio/SoloRPG - Journey 2.mp3",
  ],
};
```

### Volumes (ambiente — alinhado a `audio-engine`)

| Categoria | Volume | Rationale |
|-----------|--------|-----------|
| `menu` | 0.12 | lobby — já existente |
| `tensao` | 0.08 | já existente |
| `combate` | 0.09 | ligeiramente mais presente, ainda fundo |
| `exploracao` | 0.07 | |
| `investigacao` | 0.06 | mais discreta |
| `horror` | 0.07 | |
| `horror_caos` | 0.07 | |
| `social` | 0.06 | respiro — mais baixo |
| `jornada` | 0.06 | |

---

## Horror: dois moods, quatro faixas (dois pools)

| Mood GM | Arquivos (sorteio interno) | Foco narrativo | NÃO usar para |
|---------|----------------------------|----------------|---------------|
| `horror` | `Horror.mp3`, `Horror 2.mp3` | Sobrenatural: mortos-vivos, fantasmas, maldições, império antigo | Caos, warp, corrupção |
| `horror_caos` | `Horror Chaos.mp3`, `Horror Chaos 2.mp3` | Caos/Ruína: corrupção, mutação, símbolos profanos, warp | Horror genérico sem Caos |

O GM escolhe o **mood**; o `audioManager` sorteia uma variante **dentro** do pool. Pools de `horror` e `horror_caos` nunca se misturam.

---

## Comportamentos preservados

| Comportamento | Detalhe |
|---------------|---------|
| Sticky | `scene_mood: null` no turno → frontend não chama `setMood` |
| Idempotência | `play("combate")` com `combate` já tocando → no-op |
| Substituição | `play("exploracao")` com `tensao` tocando → stop + nova faixa |
| Mute | `setMuted(true)` invalida qualquer categoria |
| Rota | In-game moods só em `/play/`; fora → ignorado |
| Menu | `menu` só no lobby allowlist; nunca em `/play/` |
| Async safety | `playGeneration` + commit pós-`await` (regressão fix-audio-mute-routing) |

---

## Backend whitelist

```python
IN_GAME_MOODS = frozenset({
    "tensão", "combate", "exploração", "investigação",
    "horror", "horror_caos", "social", "jornada", "normal",
})

# em _handle_signal MUSICA:
mood = signal.payload.get("mood")
if mood in IN_GAME_MOODS:
    result.scene_mood = mood
```

Centralizar em constante compartilhada (ex. `app/services/audio_moods.py`) se evitar duplicação no futuro.

---

## Prompt GM — critérios resumidos

Incluir no `gm-system-prompt.md`:

1. Lista fechada de `mood` (9 valores).
2. Árvore de decisão curta:
   - Combate iniciado? → `combate`
   - Caos/warp/corrupção dominante? → `horror_caos`
   - Sobrenatural sem Caos? → `horror`
   - Perigo iminente sem luta? → `tensão`
   - Explorando com calma? → `exploração`
   - Deduzindo/vigiando? → `investigação`
   - Viagem? → `jornada`
   - Refúgio social? → `social` (raro)
   - Alívio? → `normal`
3. Reforço: `horror` ≠ `horror_caos` — não intercambiáveis.

---

## Testes planejados

| Caso | Assert |
|------|--------|
| `setMood("combate")` em `/play/` | `play("combate")` chamado |
| `setMood("horror")` | src em pool Horror (sem `Chaos`) |
| `setMood("horror_caos")` | src contém `Horror Chaos` |
| `combate` → `exploração` | uma faixa audível; categoria atualizada |
| `setMood("combate")` fora de `/play/` | no-op |
| mood desconhecido | ignorado |
| idempotência `play("social")` ×2 | 1 elemento Audio |

---

## Deploy / assets

- `npm run prepare:audio` e `COPY audio` no Docker já copiam todos os `*.mp3`.
- Opcional: estender smoke check no Dockerfile para um MP3 novo (ex. `SoloRPG - Combat.mp3`) além do Theme.
