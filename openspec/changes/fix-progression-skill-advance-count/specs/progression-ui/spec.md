# Spec: progression-ui

**Change:** `fix-progression-skill-advance-count`  
**Capability:** nova — `progression-ui` (será promovida a `openspec/specs/` no archive)

---

## ADDED Requirements

### Requirement: Progression screen MUST display accurate skill advance totals

The progression page (`/progression`) SHALL show the total current advances for each skill in the label `atual +N`, where N equals the sum of `advances` for that skill name in the character sheet.

#### Scenario: Counter increments after each purchase

- **GIVEN** the player is on `/progression` with enough XP
- **WHEN** they click to buy Percepção +1 three times in a row
- **THEN** the Percepção row shows `atual +1`, then `atual +2`, then `atual +3` after each successful purchase
- **AND** available XP decreases by 5 after each click

#### Scenario: Counter matches API after page reload

- **GIVEN** a character with Percepção at `advances: 4` in the database
- **WHEN** the player opens `/progression`
- **THEN** the Percepção button shows `atual +4` without requiring new purchases

### Requirement: Owned talents MUST display label "adquirido"

On the progression screen, talents the character already owns SHALL show the suffix `· adquirido` (not `· possuído`). The purchase button SHALL remain disabled for owned talents.

#### Scenario: Owned talent label

- **GIVEN** the character owns talent "Resolução"
- **WHEN** the progression talents list is rendered
- **THEN** the Resolução row includes `· adquirido`
- **AND** the button is disabled

#### Scenario: Affordable unowned talent

- **GIVEN** the character does not own "Robusto" and has enough XP
- **WHEN** the progression talents list is rendered
- **THEN** the row shows cost only (no `adquirido` suffix)
- **AND** the button is enabled
