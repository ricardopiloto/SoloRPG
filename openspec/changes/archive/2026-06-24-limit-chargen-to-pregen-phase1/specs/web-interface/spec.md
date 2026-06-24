## MODIFIED Requirements

### Requirement: Multi-step character creation wizard
The web application SHALL provide a multi-step character creation wizard at `/character` **when custom character creation is enabled by configuration**. When custom creation is disabled (phase 1), the wizard SHALL NOT be shown and `/character` SHALL present only pre-generated character selection.

#### Scenario: Wizard hidden in phase 1
- **WHEN** custom character creation is disabled
- **THEN** the `/character` page does not display wizard tabs or steps
- **AND** only the pre-generated character grid is shown

#### Scenario: Wizard step navigation (when enabled)
- **WHEN** custom creation is enabled and the player starts custom character creation
- **THEN** the UI displays a stepper with Species, Career, Attributes, Skills & Talents, Trappings, and Details
- **AND** prevents advancing to the next step while the current step has backend validation errors

#### Scenario: Attributes step supports roll and point-buy (when enabled)
- **WHEN** the player is on the Attributes step with custom creation enabled
- **THEN** they can choose rolled characteristics (with swap and optional reroll) or point-buy allocation
- **AND** the UI shows live totals and XP awarded from the backend preview

#### Scenario: Creation strings localized
- **WHEN** the character page or wizard is displayed
- **THEN** all labels, errors, and empty states are in PT-BR via i18n keys

### Requirement: Character page entry flow
The character page SHALL offer pre-generated selection as the primary entry path in phase 1. The guided WFRP creation wizard SHALL be available only when custom creation is enabled.

#### Scenario: Pregen-only entry in phase 1
- **WHEN** the player opens `/character` with custom creation disabled
- **THEN** pre-generated templates are listed for selection
- **AND** no free-form or wizard custom creation UI is shown

#### Scenario: Dual paths when wizard enabled
- **WHEN** custom creation is enabled
- **THEN** the player can choose between pre-generated selection and the guided wizard
- **AND** the free-form attribute/wounds/fate inputs are not shown

### Requirement: Campaign and Character Management Screens
The UI SHALL provide screens for selecting characters and campaigns. In phase 1, character acquisition SHALL emphasize the account starter character and pre-generated templates rather than custom creation.

#### Scenario: Character management access
- **WHEN** the authenticated player is not in an active session
- **THEN** they can access character and campaign management
- **AND** see only their own characters and related campaigns

#### Scenario: Empty state directs to pregens
- **WHEN** the authenticated player has no characters (edge case before starter sync)
- **THEN** the UI directs them to `/character` to select a pre-generated template
- **AND** does not offer the custom creation wizard while disabled
