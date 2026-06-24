# audio-mood-signal Specification

## Purpose
TBD - created by archiving change add-ambient-audio-engine. Update Purpose after archive.
## Requirements
### Requirement: GM MUST emit [MUSICA] signal when scene tone changes

O GM SHALL emitir o sinal `[MUSICA]` com o payload correto ao início de cenas tensas e ao retorno à normalidade.

#### Scenario: Início de cena de fuga/perseguição

- **Dado** que o personagem começa a ser perseguido por guardas
- **Quando** o GM narra a cena
- **Então** o GM emite `[MUSICA]{"mood":"tensão","descricao":"perseguição por guardas"}` junto com a narrativa

#### Scenario: Fim da cena tensa

- **Dado** que o personagem conseguiu se esconder e a tensão passou
- **Quando** o GM narra o alívio da situação
- **Então** o GM emite `[MUSICA]{"mood":"normal","descricao":"personagem está seguro"}` junto com a narrativa

#### Scenario: Cena social sem tensão

- **Dado** que o personagem está conversando numa taberna sem perigo
- **Quando** o GM narra a interação
- **Então** o GM NÃO emite `[MUSICA]` — silêncio in-game é o padrão

---

### Requirement: Backend MUST propagate scene_mood in turn responses

O backend SHALL incluir `scene_mood` no payload de resposta de turno quando o sinal `[MUSICA]` for recebido do LLM.

#### Scenario: Sinal MUSICA presente na resposta LLM

- **Dado** que a resposta do LLM contém `[MUSICA]{"mood":"tensão",...}[/MUSICA]`
- **Quando** o orchestrator processa os sinais
- **Então** `TurnResult.scene_mood = "tensão"`
- **E** o SSE `done` payload inclui `"scene_mood": "tensão"`

#### Scenario: Nenhum sinal MUSICA na resposta

- **Dado** que a resposta do LLM não contém `[MUSICA]`
- **Quando** o orchestrator processa os sinais
- **Então** `TurnResult.scene_mood = None`
- **E** o SSE `done` payload inclui `"scene_mood": null`
- **E** o frontend mantém o mood atual (sem mudança)

