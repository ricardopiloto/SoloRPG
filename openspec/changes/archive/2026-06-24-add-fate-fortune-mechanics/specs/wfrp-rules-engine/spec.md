## MODIFIED Requirements

### Requirement: Fate and Fortune Points
The system SHALL track Fate Points and Fortune Points on the character sheet. Fate Points SHALL be spendable to avoid taking a wound or to survive a lethal blow; they SHALL NOT recover between sessions or campaigns. Fortune Points SHALL be spendable only to re-roll a failed test. At the start of each new session, Fortune Points SHALL reset to the character's current Fate Point total (`fate_current`). Fortune Points SHALL NOT provide a +10 test bonus.

#### Scenario: Lethal critical with Fate Point available
- **WHEN** the GM emits `[ACAO_SISTEMA]` tipo `usar_ponto_destino` with motivo `avoid_death`
- **AND** the character has Fate Points remaining
- **THEN** the system deducts one Fate Point
- **AND** sets wounds to 1 and ignores the critical effect
- **AND** updates character state

#### Scenario: Avoid wound with Fate Point
- **WHEN** the GM emits `[ACAO_SISTEMA]` tipo `usar_ponto_destino` with motivo `avoid_wound`
- **AND** the character has Fate Points remaining
- **THEN** the system deducts one Fate Point
- **AND** does not apply the pending wound increment

#### Scenario: Lethal critical without Fate Points
- **WHEN** a lethal critical occurs and the character has zero Fate Points
- **THEN** the system processes `[ACAO_SISTEMA]` tipo `morte_personagem`
- **AND** marks the character as dead
- **AND** marks the campaign as unfinished (inacabada)

#### Scenario: Fortune re-roll on failed test
- **WHEN** a GM test fails and the character has Fortune Points remaining
- **AND** the player chooses to spend Fortune
- **THEN** the system deducts one Fortune Point
- **AND** re-executes the roll with the same target and modifiers

#### Scenario: Fortune refresh at new session
- **WHEN** a new game session starts for a character with `fate_current = N`
- **THEN** `fortune_current` and `fortune_max` are set to `N`
