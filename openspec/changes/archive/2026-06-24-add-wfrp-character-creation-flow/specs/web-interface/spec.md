## ADDED Requirements

### Requirement: Multi-step character creation wizard
The web application SHALL provide a multi-step character creation wizard at `/character` replacing the free-form custom tab, while keeping the pre-generated character selection path.

#### Scenario: Wizard step navigation
- **WHEN** the player starts custom character creation
- **THEN** the UI displays a stepper with Species, Career, Attributes, Skills & Talents, Trappings, and Details
- **AND** prevents advancing to the next step while the current step has backend validation errors

#### Scenario: Attributes step supports roll and point-buy
- **WHEN** the player is on the Attributes step
- **THEN** they can choose rolled characteristics (with swap and optional reroll) or point-buy allocation
- **AND** the UI shows live totals and XP awarded from the backend preview

#### Scenario: Skills step enforces budgets
- **WHEN** the player allocates species and career skill advances
- **THEN** the UI displays remaining points (species +3/+5 limits and career 40-point pool)
- **AND** disables continue when budgets are exceeded

#### Scenario: Final review before persist
- **WHEN** the player reaches the Details/Revisão step
- **THEN** the UI shows a read-only summary of the computed character sheet
- **AND** requires explicit confirmation before calling `POST /characters`

#### Scenario: Creation strings localized
- **WHEN** the wizard is displayed
- **THEN** all labels, errors, and empty states are in PT-BR via i18n keys

#### Scenario: AI background button on Details step
- **WHEN** the player is on the Details step
- **THEN** the UI shows a background textarea, an optional hints field, and a "Gerar com IA" button
- **AND** shows loading state while the generation request is in progress
- **AND** displays an error message if generation fails without clearing manual input

#### Scenario: Regenerate background
- **WHEN** the player clicks "Gerar com IA" again after a previous generation
- **THEN** the UI replaces the textarea content with the new generated text
- **AND** the player can still edit the result before confirming character creation

## MODIFIED Requirements

### Requirement: Character page entry flow
The character page SHALL offer pre-generated selection and the guided WFRP creation wizard as the only custom creation paths.

#### Scenario: No free-form custom form
- **WHEN** the player opens `/character` and selects custom creation
- **THEN** the free-form attribute/wounds/fate inputs are not shown
- **AND** the guided wizard is shown instead
