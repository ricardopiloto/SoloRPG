# Spec: quickroll-ux

**Change:** `add-skill-name-truncation-tooltip`  
**Capability:** `quickroll-ux` (modificada)

---

## ADDED Requirements

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
