# quickroll-ux Specification

## Purpose
TBD - created by archiving change add-skill-name-truncation-tooltip. Update Purpose after archive.
## Requirements
### Requirement: Truncated skill names MUST show a tooltip with the full name

Quando o nome de uma perícia é truncado por falta de espaço na coluna Nome, o sistema SHALL exibir um tooltip com o nome completo ao passar o mouse sobre o texto.

#### Scenario: Nome longo truncado na sidebar

- **Dado** que a perícia "Atirar (Armas de Fogo)" não cabe na coluna Nome (~240px)
- **Quando** o usuário passa o mouse sobre o nome truncado
- **Então** um tooltip nativo exibe "Atirar (Armas de Fogo)"

#### Scenario: Nome curto sem truncamento

- **Dado** que a perícia "Arrombamento" cabe integralmente na coluna Nome
- **Quando** o usuário passa o mouse sobre o nome
- **Então** nenhum tooltip é exibido

#### Scenario: Sidebar redimensionada

- **Dado** que o usuário alarga a sidebar até o nome deixar de truncar
- **Quando** o truncamento deixa de ocorrer
- **Então** o tooltip deixa de aparecer automaticamente

#### Scenario: Acessibilidade preservada

- **Dado** que o nome está truncado visualmente
- **Quando** um leitor de tela foca o botão da perícia
- **Então** o `aria-label` do botão continua anunciando o nome completo da perícia

### Requirement: Skill rows MUST display a four-column table with name, linked attribute, advances, and target

Cada perícia na sidebar SHALL ser renderizada como uma linha tabular com quatro colunas: **Nome**, **Atributo** (sigla), **Avanços** (número) e **Alvo** (valor total de rolagem).

#### Scenario: Perícia com avanços e atributo vinculado

- **Dado** que o personagem tem Dex 24, 4 avanços em "Arrombamento" (vinculada a Dex)
- **Quando** a sidebar renderiza a linha
- **Então** exibe: Nome `Arrombamento`, Atributo `Dex`, Avanços `4`, Alvo `28`

#### Scenario: Perícia sem avanços

- **Dado** que o personagem não possui avanços em "Furtividade"
- **Quando** a linha é renderizada
- **Então** a coluna Avanços exibe `0` — nunca vazia ou omitida

#### Scenario: Coluna Atributo mostra sigla, não valor

- **Dado** que "Atirar (Armas de Fogo)" está vinculada a BS com valor base 33
- **Quando** a linha é renderizada
- **Então** a coluna Atributo exibe `BS`
- **E** NÃO exibe `33` na coluna Atributo

#### Scenario: Cabeçalho da tabela

- **Dado** que a seção de perícias está expandida
- **Quando** o usuário visualiza a lista
- **Então** uma linha de cabeçalho identifica as colunas Nome, Atributo, Avanços e Alvo acima das linhas clicáveis

---

### Requirement: Name column MUST include a subtle leader line for visual association

A coluna Nome SHALL incluir uma linha tracejada quase transparente preenchendo o espaço entre o nome truncado e o início das colunas numéricas.

#### Scenario: Nome curto com leader visível

- **Dado** que a perícia tem nome curto ("Arrombamento")
- **Quando** a linha é renderizada
- **Então** uma linha tracejada sutil aparece entre o nome e a coluna Atributo
- **E** o usuário associa visualmente o nome às colunas à direita

#### Scenario: Nome longo truncado

- **Dado** que o nome da perícia é longo (ex: "Atirar (Armas de Fogo)")
- **Quando** a sidebar tem largura padrão (~240px)
- **Então** o nome trunca com reticências
- **E** as colunas Atributo, Avanços e Alvo permanecem visíveis e alinhadas com as demais linhas

---

### Requirement: Skill row accessibility MUST remain intact

O botão de quick roll SHALL manter `aria-label` descritivo mesmo com o layout tabular.

#### Scenario: Leitor de tela

- **Dado** que uma linha tabular está focada
- **Quando** o leitor de tela anuncia o botão
- **Então** o `aria-label` inclui nome da perícia, atributo, avanços e alvo numérico

### Requirement: Skill row MUST display the computed total target value

A linha de cada perícia na sidebar SHALL exibir no lado direito o valor numérico total da rolagem (atributo base + avanços), não o formato sheet `N+[ATTR]`.

#### Scenario: Perícia com avanços

- **Dado** que o personagem tem BS = 33 e 4 avanços em "Atirar (Armas de Fogo)"
- **Quando** a sidebar é renderizada
- **Então** a linha mostra `Atirar (Armas de Fogo)` à esquerda e `37` à direita

#### Scenario: Perícia sem avanços

- **Dado** que o personagem tem Ag = 34 e nenhum avanço em "Furtividade"
- **Quando** a sidebar é renderizada
- **Então** a linha mostra `Furtividade` à esquerda e `34` à direita

#### Scenario: Valor total zero (edge case)

- **Dado** que o atributo vinculado é 0 e o personagem não tem avanços na perícia
- **Quando** a sidebar é renderizada
- **Então** a linha mostra `0` à direita — nunca string vazia ou ausente

#### Scenario: Consistência com QuickRollPopover

- **Dado** que a sidebar mostra `37` para uma perícia
- **Quando** o jogador clica nessa linha e o QuickRollPopover abre
- **Então** o alvo exibido no popover (antes de qualquer modificador) é também `37`

### Requirement: QuickRollPopover MUST NOT auto-roll via countdown timer

O `QuickRollPopover` SHALL exigir ação explícita do jogador para disparar a rolagem — nenhum timer automático SHALL executar `onRoll` sem interação.

#### Scenario: Jogador abre o popover e aguarda sem clicar

- **Dado** que o jogador clicou em uma perícia ou atributo e o popover está visível
- **Quando** o jogador não clica em nenhum botão por 5 segundos
- **Então** nenhuma rolagem é disparada automaticamente
- **E** o popover permanece aberto aguardando input

#### Scenario: Jogador clica "Rolar agora"

- **Dado** que o popover está visível com um modificador configurado
- **Quando** o jogador clica no botão "Rolar agora"
- **Então** `onRoll(modifier)` é chamado imediatamente
- **E** o popover fecha

#### Scenario: Jogador clica "Cancelar"

- **Dado** que o popover está visível
- **Quando** o jogador clica em "Cancelar"
- **Então** `onCancel()` é chamado e nenhuma rolagem acontece

#### Scenario: Jogador ajusta modificador antes de rolar

- **Dado** que o popover está visível com modificador inicial 0
- **Quando** o jogador clica em "+" duas vezes (modificador = +10) e depois clica "Rolar agora"
- **Então** `onRoll(10)` é chamado com o modificador correto

