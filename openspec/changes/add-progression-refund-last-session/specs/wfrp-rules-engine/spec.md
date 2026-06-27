# Spec delta: wfrp-rules-engine

**Change:** `add-progression-refund-last-session`

---

## ADDED Requirements

### Requirement: Progression refunds SHALL reverse WFRP4e purchases server-side

Refunding a progression purchase SHALL undo the mechanical effect of that purchase in the rules engine without LLM involvement. Skill refunds SHALL decrement advances; talent refunds SHALL remove the talent from the character sheet.

#### Scenario: Refund skill advance

- **GIVEN** a character has Percepção with `advances: 3`
- **WHEN** a refundable skill purchase for Percepção +1 is refunded
- **THEN** Percepção advances become 2
- **AND** `xp_spent` decreases by the purchase cost (5 XP)

#### Scenario: Refund removes skill at zero advances

- **GIVEN** a character bought their first Percepção advance in the current window (`advances: 1`)
- **WHEN** that purchase is refunded
- **THEN** the Percepção skill entry is removed from the skills list
- **AND** `xp_spent` decreases by 5

#### Scenario: Refund talent

- **GIVEN** a character owns talent "Robusto" from a refundable purchase
- **WHEN** that purchase is refunded
- **THEN** "Robusto" is removed from `talents`
- **AND** `xp_spent` decreases by 10

#### Scenario: FIFO attribution caps refundable XP per session award

- **GIVEN** the last session awarded 50 XP and the refund budget starts at 50
- **WHEN** the player makes sequential purchases totaling 60 XP after session end
- **THEN** the sum of `refundable_xp` across non-refunded ledger entries SHALL NOT exceed 50
- **AND** purchases made after the budget reaches 0 SHALL have `refundable_xp = 0`

#### Scenario: Invalid refund rejected

- **WHEN** a refund is requested for a purchase that is already refunded, has `refundable_xp = 0`, or belongs to a closed window
- **THEN** the API returns 400 with a clear error
- **AND** character state remains unchanged
