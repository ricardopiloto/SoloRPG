# Spec delta: audio-mood-signal

**Change:** `expand-audio-mood-vocabulary`

---

## MODIFIED Requirements

### Requirement: GM MUST emit [MUSICA] signal when scene tone changes

O GM SHALL emitir o sinal `[MUSICA]` com o payload correto quando o **tom emocional da cena muda** durante a sessão in-game. Os valores de `mood` permitidos são:

`tensão`, `combate`, `exploração`, `investigação`, `horror`, `horror_caos`, `social`, `jornada`, `normal`.

O GM MUST NOT emitir `[MUSICA]` em cenas neutras sem mudança de tom — silêncio in-game permanece o padrão até o primeiro sinal.

#### Scenario: Início de cena de fuga/perseguição

- **Dado** que o personagem começa a ser perseguido por guardas
- **Quando** o GM narra a cena
- **Então** o GM emite `[MUSICA]{"mood":"tensão","descricao":"perseguição por guardas"}` junto com a narrativa

#### Scenario: Combate iniciado

- **Dado** que o combate mecânico começou (iniciativa ou primeiro turno de luta)
- **Quando** o GM narra a abertura do combate
- **Então** o GM emite `[MUSICA]{"mood":"combate","descricao":"..."}`

#### Scenario: Horror sobrenatural sem Caos

- **Dado** que a cena foca em mortos-vivos, espectros ou maldição antiga **sem** corrupção do Caos
- **Quando** o tom muda para horror sobrenatural
- **Então** o GM emite `[MUSICA]{"mood":"horror","descricao":"..."}`
- **E** NÃO usa `horror_caos` para essa cena

#### Scenario: Horror do Caos

- **Dado** que a cena foca em warp, corrupção, mutação ou rituais profanos do Caos
- **Quando** o tom muda para horror do Caos
- **Então** o GM emite `[MUSICA]{"mood":"horror_caos","descricao":"..."}`
- **E** NÃO usa `horror` genérico quando o Caos é o elemento dominante

#### Scenario: Fim da cena com tom emocional

- **Dado** que a trilha in-game está ativa (qualquer mood exceto silêncio)
- **Quando** o GM narra alívio ou fim do tom (refúgio, ameaça passou)
- **Então** o GM emite `[MUSICA]{"mood":"normal","descricao":"..."}`

#### Scenario: Cena social sem mudança de tom

- **Dado** que o personagem está conversando numa taberna sem perigo e **sem** transição de tom
- **Quando** o GM narra a interação
- **Então** o GM NÃO emite `[MUSICA]` — silêncio in-game é o padrão até transição explícita

---

### Requirement: Backend MUST propagate scene_mood in turn responses

O backend SHALL incluir `scene_mood` no payload de resposta de turno quando o sinal `[MUSICA]` for recebido do LLM com `mood` na whitelist in-game.

Moods aceitos: `tensão`, `combate`, `exploração`, `investigação`, `horror`, `horror_caos`, `social`, `jornada`, `normal`.

#### Scenario: Sinal MUSICA com combate

- **Dado** que a resposta do LLM contém `[MUSICA]{"mood":"combate",...}[/MUSICA]`
- **Quando** o orchestrator processa os sinais
- **Então** `TurnResult.scene_mood = "combate"`
- **E** o SSE `done` payload inclui `"scene_mood": "combate"`

#### Scenario: Sinal MUSICA com horror_caos

- **Dado** que a resposta do LLM contém `[MUSICA]{"mood":"horror_caos",...}[/MUSICA]`
- **Quando** o orchestrator processa os sinais
- **Então** `TurnResult.scene_mood = "horror_caos"`

#### Scenario: Mood inválido ignorado

- **Dado** que a resposta contém `[MUSICA]{"mood":"tenso",...}[/MUSICA]` (valor fora da whitelist)
- **Quando** o orchestrator processa os sinais
- **Então** `TurnResult.scene_mood` permanece inalterado ou `None`
- **E** nenhum erro é exposto ao jogador

#### Scenario: Nenhum sinal MUSICA na resposta

- **Dado** que a resposta do LLM não contém `[MUSICA]`
- **Quando** o orchestrator processa os sinais
- **Então** `TurnResult.scene_mood = None`
- **E** o SSE `done` payload inclui `"scene_mood": null`
- **E** o frontend mantém o mood atual (sem mudança)
