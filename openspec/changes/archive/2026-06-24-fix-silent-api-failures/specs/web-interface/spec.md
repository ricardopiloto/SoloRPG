## ADDED Requirements

### Requirement: Visible API error feedback on core pages
The home, campaigns, and character pages SHALL display a user-visible error message when initial data loading or create actions fail due to API errors, instead of failing silently with empty state.

#### Scenario: Load failure on campaigns page
- **WHEN** `GET /characters` or `GET /campaigns` fails
- **THEN** the campaigns page displays an error message explaining the failure
- **AND** the user is not left with an empty screen that appears functional

#### Scenario: Character creation failure
- **WHEN** the user clicks a pregen or submits custom character creation and the API returns an error
- **THEN** an error message is shown on the character page
- **AND** the user understands the action failed
