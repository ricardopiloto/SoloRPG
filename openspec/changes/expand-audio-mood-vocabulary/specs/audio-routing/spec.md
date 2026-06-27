# Spec delta: audio-routing

**Change:** `expand-audio-mood-vocabulary`

---

## MODIFIED Requirements

### Requirement: Tension tracks MUST play when LLM signals tension

Trilhas in-game SHALL tocar apenas quando o pathname está sob `/play/` **e** o turn response inclui `scene_mood` com um mood in-game válido (exceto `normal`, que para a reprodução). Fora de `/play/`, qualquer `scene_mood` in-game MUST be ignored.

Moods in-game que iniciam trilha: `tensão`, `combate`, `exploração`, `investigação`, `horror`, `horror_caos`, `social`, `jornada`.

Cada mood SHALL mapear para faixas em `audio/` conforme catálogo do projeto. `horror` e `horror_caos` são moods **distintos** com pools dedicados: `horror` sorteia entre `SoloRPG - Horror.mp3` e `Horror 2.mp3`; `horror_caos` sorteia entre `Horror Chaos.mp3` e `Horror Chaos 2.mp3`. Os pools MUST NOT se misturar.

#### Scenario: GM emite tensão durante sessão

- **Dado** que o jogador está em `/play/{sessionId}` com som ativo
- **Quando** o SSE `done` retorna `scene_mood: "tensão"`
- **Então** a trilha de tensão toca em loop com volume ambiente baixo

#### Scenario: GM emite combate durante sessão

- **Dado** que o jogador está em `/play/{sessionId}` com som ativo
- **Quando** o SSE `done` retorna `scene_mood: "combate"`
- **Então** a trilha Combat toca em loop

#### Scenario: GM emite horror sobrenatural

- **Dado** que o jogador está em `/play/{sessionId}` com som ativo
- **Quando** o SSE `done` retorna `scene_mood: "horror"`
- **Então** o sistema reproduz uma faixa do pool `Horror` / `Horror 2` (nunca `Horror Chaos`)

#### Scenario: GM emite horror do Caos

- **Dado** que o jogador está em `/play/{sessionId}` com som ativo
- **Quando** o SSE `done` retorna `scene_mood: "horror_caos"`
- **Então** o sistema reproduz uma faixa do pool `Horror Chaos` / `Horror Chaos 2` (nunca `Horror.mp3` ou `Horror 2.mp3` do pool sobrenatural)

#### Scenario: GM encerra mood in-game

- **Dado** que qualquer trilha in-game está tocando em `/play/{sessionId}`
- **Quando** o response inclui `scene_mood: "normal"`
- **Então** a reprodução para

#### Scenario: Troca de mood sem passar por normal

- **Dado** que a trilha `combate` está tocando
- **Quando** o response inclui `scene_mood: "exploração"`
- **Então** a trilha de combate para e a trilha de exploração inicia
- **E** no máximo uma faixa audível permanece ativa

#### Scenario: scene_mood in-game fora de sessão ignorado

- **Dado** que o jogador está em `/campaigns`
- **Quando** um response hipotético incluiria `scene_mood: "combate"`
- **Então** nenhuma trilha in-game inicia

#### Scenario: Turn response sem scene_mood (sticky)

- **Dado** que a trilha `investigação` está tocando
- **Quando** o turn response não inclui `scene_mood`
- **Então** a trilha de investigação continua

---

## ADDED Requirements

### Requirement: In-game mood tracks MUST use ambient volume levels

Cada categoria in-game SHALL usar volume fixo baixo (ambiente, não foreground), conforme `Docs/audio-engine.md`. Valores implementados: `tensao` 0.08, `combate` 0.09, `exploracao`/`horror`/`horror_caos` 0.07, `investigacao`/`social`/`jornada` 0.06.

#### Scenario: Combate não domina a UI

- **Dado** que a trilha `combate` está tocando
- **Quando** o jogador lê a narrativa no chat
- **Então** o volume permanece ≤ 0.09 (9% do máximo do elemento audio)

### Requirement: Dual-variant categories MUST pick randomly

Para categorias com dois MP3 (`combate`, `exploracao`, `investigacao`, `horror`, `horror_caos`, `social`, `jornada`, `tensao`, `menu`), o `audioManager` SHALL escolher aleatoriamente uma variante ao iniciar reprodução dentro do pool da categoria. Pools `horror` e `horror_caos` SHALL NOT sortear entre si.

#### Scenario: Duas sessões de combate podem ter variantes diferentes

- **Dado** que o jogador inicia `combate` em duas sessões distintas
- **Quando** `play("combate")` é chamado em cada uma
- **Então** o sistema pode selecionar `Combat.mp3` ou `Combat 2.mp3` independentemente por sessão
