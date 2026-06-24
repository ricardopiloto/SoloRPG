# Spec: quickroll-ux

**Change:** `remove-quickroll-countdown`  
**Capability:** `quickroll-ux` (modificada)

---

## ADDED Requirements

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
