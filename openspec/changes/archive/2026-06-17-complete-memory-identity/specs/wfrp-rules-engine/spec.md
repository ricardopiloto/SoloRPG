## ADDED Requirements

### Requirement: Fortune Point Expenditure
The system SHALL implement WFRP4e Fortune Point spending rules server-side, distinct from Fate Points, and expose expenditure via `[ACAO_SISTEMA]` or dedicated signals.

#### Scenario: Fortune point spent
- **WHEN** a Fortune Point expenditure is triggered by game rules
- **THEN** the system deducts one Fortune Point if available
- **AND** applies the mechanical benefit
- **AND** updates character state before next LLM turn
