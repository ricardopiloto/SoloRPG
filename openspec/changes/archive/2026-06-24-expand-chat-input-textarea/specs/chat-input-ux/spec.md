# Spec: chat-input-ux

**Change:** `expand-chat-input-textarea`  
**Capability:** `chat-input-ux` (modificada)

---

## ADDED Requirements

### Requirement: Chat input MUST grow vertically to keep all typed text visible

O campo de ação do jogador SHALL ser um `<textarea>` que expande verticalmente conforme o conteúdo, de forma que todo o texto digitado esteja sempre visível sem scroll horizontal.

#### Scenario: Texto curto (1 linha)

- **Dado** que o jogador digita "Avanço em direção à porta"
- **Quando** o texto cabe em uma linha
- **Então** o campo exibe 1 linha de altura — igual ao campo anterior

#### Scenario: Texto longo (múltiplas linhas visuais)

- **Dado** que o jogador digita uma ação longa com mais de 80 caracteres
- **Quando** o texto ultrapassa a largura do campo
- **Então** o campo cresce verticalmente, quebrando o texto em múltiplas linhas visuais
- **E** todo o texto permanece visível sem scroll horizontal

#### Scenario: Texto muito longo (acima do máximo)

- **Dado** que o jogador digita um texto que excede `max-height` (≈4 linhas)
- **Quando** o campo atinge o limite de altura
- **Então** o campo para de crescer e adiciona scroll vertical interno
- **E** o texto continua acessível via scroll dentro do campo

---

### Requirement: Enter key MUST submit; Shift+Enter MAY add a line break

O campo SHALL interpretar Enter (sem Shift) como envio da ação, preservando o comportamento atual do `<input>`.

#### Scenario: Jogador pressiona Enter

- **Dado** que há texto no campo e o botão está habilitado
- **Quando** o jogador pressiona Enter (sem Shift)
- **Então** a ação é enviada — equivalente a clicar no botão "→"

#### Scenario: Jogador pressiona Shift+Enter

- **Dado** que o jogador quer revisar a ação antes de enviar
- **Quando** o jogador pressiona Shift+Enter
- **Então** uma nova linha literal é adicionada ao campo (comportamento padrão de textarea)
- **E** nenhum envio ocorre

---

### Requirement: Campo MUST resetar para 1 linha após o envio

Após o envio da ação, o campo SHALL voltar à altura mínima (1 linha) para o próximo input.

#### Scenario: Após envio de ação longa

- **Dado** que o jogador enviou uma ação que ocupava 3 linhas no campo
- **Quando** o envio é completado
- **Então** o campo retorna a 1 linha de altura
- **E** está vazio e pronto para o próximo input
