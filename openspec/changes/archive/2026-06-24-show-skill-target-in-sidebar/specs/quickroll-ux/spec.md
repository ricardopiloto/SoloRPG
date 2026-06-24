# Spec: quickroll-ux

**Change:** `show-skill-target-in-sidebar`  
**Capability:** `quickroll-ux` (modificada)

---

## ADDED Requirements

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
