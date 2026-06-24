# Spec: quickroll-ux

**Change:** `refine-skill-row-leader-line`  
**Capability:** `quickroll-ux` (modificada)

---

## ADDED Requirements

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
