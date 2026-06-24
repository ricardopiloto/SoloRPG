# Spec: audio-routing

**Change:** `add-ambient-audio-engine`  
**Capability:** `audio-routing` (nova)

---

## ADDED Requirements

### Requirement: Theme tracks MUST play on non-game pages

O sistema SHALL iniciar a reprodução de um track da categoria `menu` em loop quando o usuário estiver em qualquer rota fora de `/play/[sessionId]`.

#### Scenario: Usuário acessa a página de login

- **Dado** que o usuário abre a aplicação na página de login (sem interação anterior)
- **Quando** o usuário clica em qualquer elemento interativo pela primeira vez
- **Então** um track da categoria `menu` começa a tocar em loop
- **E** continua tocando até o usuário entrar em uma sessão ou fazer logout

#### Scenario: Usuário navega entre páginas fora de jogo

- **Dado** que o theme track está tocando na página de campanhas
- **Quando** o usuário navega para a página de personagem
- **Então** o mesmo track continua sem interrupção (mudança de rota não reinicia)

#### Scenario: Usuário entra em uma sessão de jogo

- **Dado** que o theme track está tocando
- **Quando** o usuário navega para `/play/[sessionId]`
- **Então** o áudio para imediatamente
- **E** nenhum track começa automaticamente

---

### Requirement: Audio MUST stop on logout

O sistema SHALL parar qualquer áudio em reprodução quando o usuário fizer logout.

#### Scenario: Logout com theme tocando

- **Dado** que o theme está tocando na página de campanhas
- **Quando** o usuário clica em logout
- **Então** o áudio para imediatamente

---

### Requirement: Tension tracks MUST play when LLM signals tension

O sistema SHALL iniciar um track da categoria `tensão` quando receber `scene_mood: "tensão"` na resposta do turno.

#### Scenario: GM sinaliza cena tensa

- **Dado** que a sessão está em andamento (silêncio)
- **Quando** o turn response inclui `scene_mood: "tensão"`
- **Então** um track da categoria `tensão` começa a tocar em loop

#### Scenario: GM sinaliza retorno ao normal

- **Dado** que um track de tensão está tocando
- **Quando** o turn response inclui `scene_mood: "normal"`
- **Então** o áudio para

#### Scenario: Turn response sem scene_mood

- **Dado** que um track de tensão está tocando
- **Quando** o turn response não inclui `scene_mood`
- **Então** o track atual continua — mood é "sticky" até mudança explícita

---

### Requirement: All tracks MUST loop infinitely

Qualquer track iniciado SHALL reproduzir em loop contínuo até ser parado ou substituído.

#### Scenario: Track chega ao fim

- **Dado** que um track está tocando
- **Quando** o arquivo de áudio chega ao fim
- **Então** o track reinicia automaticamente do início
