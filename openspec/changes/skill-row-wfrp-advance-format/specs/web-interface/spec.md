## MODIFIED Requirements

### Requirement: Character Sidebar Stats Layout
The left sidebar skills collapsible section SHALL display each catalog skill row with the skill name, linked attribute abbreviation in brackets, and owned skill advances when greater than zero, matching the inventory row layout pattern. When advances are greater than zero, the meta label SHALL use WFRP sheet order `{N}+[{Attr}]` (e.g. `4+[Fel]`). When advances are zero, the meta label SHALL show only `[{Attr}]`.

#### Scenario: Skill row shows WFRP advance format

- **WHEN** the player views a skill row for "Atirar (Arco)" linked to BS with 5 advances on the character sheet
- **AND** the character's BS attribute value is 33
- **THEN** the row displays the skill name and meta label `5+[BS]`
- **AND** clicking the row opens quick roll with target 38 (33 + 5)

#### Scenario: Skill row without advances

- **WHEN** the player views a catalog skill with zero advances (unowned or owned at +0)
- **THEN** the row displays only the linked attribute tag such as `[Ag]`
- **AND** no `+0`, `0+`, or numeric zero prefix is shown

#### Scenario: Skill row meta alignment

- **WHEN** the skills collapsible section is expanded
- **THEN** skill names align left and attribute/advance meta aligns right on each row
- **AND** the row remains rollable with hover feedback per ux-spec

#### Scenario: Accessible skill row label

- **WHEN** assistive technology focuses a skill row
- **THEN** the accessible name includes skill name, linked attribute, advances if any, and computed target number
