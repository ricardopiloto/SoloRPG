## ADDED Requirements

### Requirement: Known NPC roster in Personagem tab
The Personagem tab in the right session sidebar SHALL display a read-only list of NPCs the player character has interacted with in the active campaign, showing the name the character knows them by and the location associated with the encounter.

#### Scenario: NPC row shows known name and location
- **WHEN** the player opens the Personagem tab during an active session
- **AND** the campaign has an NPC record with known name "Greta, a estalajadeira" and met location "Estalagem do Corvo"
- **THEN** the sidebar displays "Greta, a estalajadeira" prominently
- **AND** displays "Estalagem do Corvo" as secondary muted text

#### Scenario: Fallback to NPC name when known_name absent
- **WHEN** an NPC has no `known_name` stored
- **THEN** the roster displays `NPC.name` as the primary label

#### Scenario: Empty NPC roster
- **WHEN** the campaign has no NPC records yet
- **THEN** the Personagem tab shows an empty-state message in PT-BR
- **AND** does not show a broken or blank panel without explanation

#### Scenario: Initial campaign NPCs include opening location
- **WHEN** a campaign is created via `[NOVA_CAMPANHA]` with initial NPCs and an opening location
- **THEN** those NPCs appear in the roster with `met_location` set to the campaign opening location unless overridden by GM payload

## MODIFIED Requirements

### Requirement: Character Diary Presentation
The Personagem tab in the right sidebar SHALL prioritize the known-NPC roster as its primary content. Personal diary entries MAY be added below the roster in a future change but are not required for MVP.

#### Scenario: Personagem tab content
- **WHEN** the player selects the Personagem tab
- **THEN** the known-NPC roster is visible and scrollable
- **AND** the layout matches the visual density of the Rolagens and Campanha tabs

## ADDED Requirements

### Requirement: Campaign NPC list API
The backend SHALL expose `GET /campaigns/{campaign_id}/npcs` returning all NPC records for the campaign with name, known_name, met_location, role, and relationship_status.

#### Scenario: List campaign NPCs
- **WHEN** the client requests NPCs for a valid campaign
- **THEN** the response includes all NPC rows for that campaign sorted alphabetically by display name
