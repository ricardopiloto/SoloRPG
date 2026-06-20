## ADDED Requirements

### Requirement: Quick Roll from Character Sidebar
During an active session, the left sidebar SHALL allow the player to initiate a d100 roll by clicking a rollable attribute, skill, or weapon entry, opening a quick-roll popover with target number, modifier controls, and confirm/cancel actions.

#### Scenario: Open quick roll popover
- **WHEN** the player clicks a rollable skill in the character sidebar
- **THEN** a popover displays the skill name and computed target number
- **AND** modifier buttons allow adjustment between -30 and +30

#### Scenario: Execute quick roll
- **WHEN** the player confirms "Rolar agora" in the quick-roll popover
- **THEN** the backend performs a server-side d100 roll with the selected modifier
- **AND** the dice overlay displays the result above the chat
- **AND** a system roll message appears in the chat log

#### Scenario: Quick roll blocked during GM test
- **WHEN** a GM-requested test is pending in the chat
- **THEN** sidebar quick-roll interactions are disabled
- **AND** the player must resolve the test block first

## MODIFIED Requirements

### Requirement: Character Sidebar Stats Layout
The left sidebar SHALL display character stats including name, career, attributes, wounds bar, Fate/Fortune Points, collapsible skills/talents/inventory, session mode with timer, and rollable indicators on attributes, skills, and weapons eligible for quick roll.

#### Scenario: Rollable skill indicator
- **WHEN** the player views skills in the collapsible section
- **THEN** skills with valid targets show as clickable rollable entries
- **AND** hover state indicates interactivity per ux-spec
