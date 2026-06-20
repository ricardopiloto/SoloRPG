## MODIFIED Requirements

### Requirement: NPC and Hook Tracking
The system SHALL maintain active NPC records (name, known name, met location, faction, relationship, status) updated from campaign creation and session summaries.

#### Scenario: NPC relationship change
- **WHEN** `[FIM_SESSAO]` reports an NPC in `npcs_interagidos`
- **THEN** the system creates or updates the NPC record
- **AND** persists optional `nome_conhecido` and `local` when provided

#### Scenario: Session end NPC location
- **WHEN** `[FIM_SESSAO]` includes `"local": "Praça do Mercado"` for an NPC
- **THEN** the NPC's `met_location` is stored or updated
- **AND** the value is returned by `GET /campaigns/{id}/npcs`
