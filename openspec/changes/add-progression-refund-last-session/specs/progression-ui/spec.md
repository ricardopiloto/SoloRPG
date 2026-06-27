# Spec delta: progression-ui

**Change:** `add-progression-refund-last-session`

---

## ADDED Requirements

### Requirement: Progression screen MUST expose refundable purchases from the last session

When a progression refund window is active (`progression_source_session_id` set after the latest session end), the `/progression` page SHALL list purchases from the current window that have `refundable_xp > 0` and are not yet refunded, each with an explicit **Devolver** control.

#### Scenario: Refundable skill purchase shown

- **GIVEN** the player bought Percepção +1 after the last session ended and the purchase has `refundable_xp = 5`
- **WHEN** the player opens `/progression`
- **THEN** the UI shows the purchase in a refundable section with label describing the advance and cost
- **AND** a **Devolver** button is enabled

#### Scenario: Successful refund updates UI

- **GIVEN** a refundable Percepção +1 purchase is listed
- **WHEN** the player clicks **Devolver** and the API succeeds
- **THEN** available XP increases
- **AND** the skill row shows decremented `atual +N`
- **AND** the refunded purchase disappears from the refundable list

#### Scenario: Non-refundable purchase hidden from refund section

- **GIVEN** a purchase with `refundable_xp = 0` (spent from older XP pool)
- **WHEN** the progression page renders
- **THEN** the purchase SHALL NOT appear in the refundable section
- **AND** no **Devolver** control is shown for it

#### Scenario: No refund section when window inactive

- **GIVEN** the player has not ended a session recently, or already started a new session
- **WHEN** `/progression` loads with `progression_window_active = false`
- **THEN** the refundable purchases section SHALL NOT be displayed

### Requirement: Progression screen MUST show remaining refundable budget

While the refund window is active, the UI SHALL display how much XP from the last session award remains attributable to refundable purchases (e.g. "35 / 50 XP reembolsáveis").

#### Scenario: Budget decreases after purchase

- **GIVEN** the last session awarded 50 XP and the refund budget is 50
- **WHEN** the player buys a 5 XP skill advance with full refundable attribution
- **THEN** the UI shows 45 XP remaining in the refundable budget

#### Scenario: Budget restores after refund

- **GIVEN** a 5 XP refundable purchase was refunded
- **WHEN** the UI refreshes progression options
- **THEN** the refundable budget increases by 5 relative to its pre-refund value
