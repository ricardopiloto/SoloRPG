## ADDED Requirements

### Requirement: Asynchronous Scene Image Generation
When the GM emits `[IMAGEM]`, the system SHALL queue image generation asynchronously via Flux 1.1 Pro. Image generation SHALL NOT block narrative text delivery to the player.

#### Scenario: Scene image requested during narration
- **WHEN** the GM emits `[IMAGEM]` with tipo "cena" during a turn
- **THEN** the narrative text streams to the player immediately
- **AND** image generation runs in a background queue
- **AND** the UI displays a thematic placeholder until the image is ready

#### Scenario: Image generation completes
- **WHEN** the Flux API returns a generated image
- **THEN** the UI replaces the placeholder with the scene illustration
- **AND** caches the image URL linked to the campaign/session

### Requirement: Image Types
The system SHALL support image types from `[IMAGEM]`: cena, personagem, mapa, and item. Each type SHALL use appropriate display placement in the UI.

#### Scenario: Map image revelation
- **WHEN** the GM emits `[IMAGEM]` with tipo "mapa"
- **THEN** the system adds or updates a map region in the map panel
- **AND** reveals only explored areas progressively as new map signals arrive

#### Scenario: Item illustration
- **WHEN** the GM emits `[IMAGEM]` with tipo "item" for a significant item
- **THEN** the system associates the image with the inventory item
- **AND** displays it in the visual inventory panel

### Requirement: Narrative Priority Images
Images with prioridade "marco" SHALL be prioritized in the generation queue over prioridade "normal" images.

#### Scenario: Marco scene during climax
- **WHEN** the GM emits `[IMAGEM]` with prioridade "marco"
- **THEN** the system prioritizes this job in the generation queue
- **AND** still does not block narrative text delivery

### Requirement: Image Caching
The system SHALL cache generated images for recurring scene types (taverna, forest, city, dungeon) to reduce generation cost and latency on similar scenes.

#### Scenario: Recurring tavern scene
- **WHEN** a new `[IMAGEM]` request semantically matches a cached tavern scene for the campaign
- **THEN** the system may serve the cached image instead of generating a new one
- **AND** still updates the UI scene display

### Requirement: Visual Inventory
The system SHALL display character trappings/inventory with visual representations linked to item records and optional item-type images.

#### Scenario: Inventory panel display
- **WHEN** the player opens the inventory panel
- **THEN** the UI shows items from the character's trappings with names, encumbrance, and visual icons or generated images where available
- **AND** reflects real-time changes from session events

### Requirement: Progressive Map Revelation
The map panel SHALL reveal areas progressively as the player explores. Map data SHALL originate from LLM `[IMAGEM]` tipo "mapa" signals, not from player direct map interaction.

#### Scenario: New area explored
- **WHEN** the player explores a new location and the GM emits a map image signal
- **THEN** the map panel adds the newly discovered region
- **AND** previously unexplored areas remain hidden or fogged

#### Scenario: Map is not a game control
- **WHEN** the player views the map panel
- **THEN** the map is display-only with no click-to-move or mouse-based navigation controls
