## ADDED Requirements

### Requirement: Character Diary Presentation
The character diary tab in the right sidebar SHALL display read-only personal-perspective entries distinct from the campaign event log, sourced from identity-layer diary data when available.

#### Scenario: Character diary entries
- **WHEN** the backend provides character diary entries for the active campaign
- **THEN** the Personagem tab shows italic or quoted personal reflections
- **AND** entries are visually distinct from campaign session summaries

### Requirement: Fate Points Gem Display
Fate Points SHALL be rendered as visual gem indicators (filled ◆ for remaining, empty ◇ for spent) in the character sidebar, not as plain numeric text alone.

#### Scenario: Fate point spent
- **WHEN** the character spends a Fate Point during a session
- **THEN** one gem changes from filled to empty in the sidebar
- **AND** the remaining count matches backend state
