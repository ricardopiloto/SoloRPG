# Spec delta: character-management

**Change:** `add-progression-refund-last-session`

---

## MODIFIED Requirements

### Requirement: Between-Session Progression

The player SHALL spend earned XP between sessions to purchase skill advances, talents, and career advances via a dedicated interface without LLM involvement. The system SHALL allow **refunding** purchases made after the most recently ended session, limited to XP attributed from that session's award (`GameSession.xp_awarded`). Refunds SHALL NOT be available after the player starts a new session for the same campaign.

#### Scenario: Progression after session with XP

- **WHEN** a session ends and the character has unspent XP
- **THEN** the system presents available advances per WFRP4e rules
- **AND** applies purchases immediately upon confirmation
- **AND** blocks progression during an active non-pausable session

#### Scenario: Refund window opens on session end

- **WHEN** a session ends with `xp_awarded` of 50
- **THEN** the character's progression refund budget SHALL be set to 50
- **AND** the progression purchase ledger for that window SHALL be empty
- **AND** subsequent purchases MAY be recorded as refundable up to the remaining budget (FIFO attribution)

#### Scenario: Refund restores XP and reverses advance

- **GIVEN** the player bought Percepção +1 (5 XP) after the last session ended with a refundable attribution of 5 XP
- **WHEN** the player requests a refund for that purchase
- **THEN** `xp_spent` decreases by 5 and available XP increases by 5
- **AND** Percepção advances decrease by 1 (or the skill entry is removed if advances reach 0)
- **AND** the progression refund budget increases by the purchase's `refundable_xp`

#### Scenario: Purchases with older XP are not refundable

- **GIVEN** the refund budget from the last session is exhausted
- **WHEN** the player spends additional XP from prior sessions
- **THEN** those purchases SHALL have `refundable_xp = 0`
- **AND** the system SHALL NOT offer a refund action for them

#### Scenario: Refund window closes on new session

- **WHEN** the player starts a new session for the campaign
- **THEN** the progression refund window SHALL close
- **AND** prior purchases SHALL NOT be refundable via the API
