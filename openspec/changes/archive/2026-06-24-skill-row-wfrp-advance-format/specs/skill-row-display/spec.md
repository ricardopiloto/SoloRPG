# Spec: skill-row-display

**Capability:** Formato WFRP de avanços + atributo na sidebar de perícias

---

## ADDED Requirements

### Requirement: SKILL-ROW-01 — Meta WFRP com avanços e atributo

Cada linha de perícia na sidebar SHALL exibir avanços antes do atributo vinculado, no padrão WFRP de ficha.

#### Scenario: Perícia com avanços

- **WHEN** o jogador visualiza uma perícia com 4 avanços vinculada a Fel
- **THEN** a meta da linha SHALL exibir `4+[Fel]`
- **AND** o quick roll SHALL usar alvo `atributo + avanços + modificador`

#### Scenario: Perícia sem avanços

- **WHEN** o jogador visualiza uma perícia com 0 avanços vinculada a Ag
- **THEN** a meta SHALL exibir apenas `[Ag]`
- **AND** SHALL NOT exibir `0+`, `+0`, ou prefixo numérico zero

#### Scenario: Perícia do catálogo não possuída

- **WHEN** o jogador visualiza perícia presente no catálogo mas ausente na ficha
- **THEN** a meta SHALL exibir `[{linked_attribute}]` do catálogo
- **AND** o alvo de quick roll SHALL ser valor do atributo + 0 avanços

#### Scenario: Layout e acessibilidade

- **WHEN** a seção colapsável de perícias está expandida
- **THEN** o nome da perícia SHALL alinhar à esquerda e a meta à direita
- **AND** o `aria-label` SHALL incluir nome, atributo, avanços (se houver), e alvo calculado
