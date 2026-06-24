## MODIFIED Requirements

### Requirement: Character Sidebar Stats Layout
The left sidebar SHALL display character stats including name, career, attributes as compact cards, wounds bar, Fate/Fortune Points, a collapsible skills section listing all catalog skills, collapsible inventory, session mode with timer, and rollable indicators on attributes, skills, and weapons eligible for quick roll.

#### Scenario: Attribute cards in compact 5×2 grid
- **WHEN** the player views the attributes section in the character sidebar
- **THEN** ten attribute cards are arranged in a fixed 2-row by 5-column grid
- **AND** cards are compact enough to remain fully visible within the sidebar without breaking layout or requiring horizontal scroll

#### Scenario: Attribute card anatomy
- **WHEN** the player views a single attribute card
- **THEN** the WFRP abbreviation (WS, BS, S, T, I, Ag, Dex, Int, WP, Fel) appears smaller at the top of the card
- **AND** the numeric characteristic value appears larger and centered below the abbreviation
- **AND** the tens digit of the value is lightly underlined to indicate the WFRP characteristic bonus (e.g. value 34 renders as underlined "3" followed by "4")
- **AND** cards appear in fixed abbreviation order regardless of object key order

#### Scenario: Attribute tooltip with full name
- **WHEN** the player hovers or focuses an attribute card
- **THEN** a tooltip displays the full English attribute name (e.g. WS → "Weapon Skill", BS → "Ballistic Skill")
- **AND** assistive technology receives an accessible label including abbreviation, full name, and value

#### Scenario: Rollable attribute card
- **WHEN** the player clicks an attribute card outside a pending GM test
- **THEN** the quick-roll popover opens with the attribute target number
- **AND** the card hover state indicates interactivity per ux-spec

#### Scenario: Skills collapsible section matches inventory pattern
- **WHEN** the player views the skills area in the character sidebar
- **THEN** skills are rendered inside a `CollapsibleSection` with the same trigger pattern as Inventory (`collapsible-trigger`, expand/collapse `−`/`+`)
- **AND** the section lists all skills from the server skill catalog, not only skills currently owned by the character
- **AND** each skill row is a rollable button with skill name on the left
- **AND** owned skills with advances show `+N` on the right in muted text

#### Scenario: Rollable skill row opens quick roll
- **WHEN** the player clicks a skill row in the collapsible skills section outside a pending GM test
- **THEN** the quick-roll popover opens with the computed target for that skill
- **AND** hover state indicates interactivity per ux-spec

#### Scenario: Quick roll unowned skill
- **WHEN** the player clicks a catalog skill the character does not possess in the collapsible list
- **THEN** the target number equals the linked attribute value with zero skill advances plus any modifier
- **AND** the backend accepts the roll without requiring the skill on the character sheet

#### Scenario: Quick roll blocked during GM test
- **WHEN** a GM-requested test is pending in the chat
- **THEN** attribute cards and skill list quick-roll controls are disabled
- **AND** the player must resolve the test block first
