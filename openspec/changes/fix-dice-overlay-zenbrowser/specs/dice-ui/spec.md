## MODIFIED Requirements

### Requirement: DiceBox initialization before roll

The system SHALL complete DiceBox initialization (or determine permanent failure) before invoking `roll()` on a player-triggered dice animation.

#### Scenario: Roll waits for init

- **WHEN** the player triggers a dice roll while DiceBox is still initializing
- **THEN** the UI SHALL show a loading state
- **AND** SHALL invoke `roll()` only after init succeeds
- **AND** SHALL NOT throw "not ready" to the console under normal timing

#### Scenario: Init failure uses fallback

- **WHEN** DiceBox init fails (missing assets, WebGL unavailable, worker error)
- **THEN** the system SHALL use the existing RNG fallback
- **AND** SHALL complete the game flow without freezing

#### Scenario: Container has non-zero size at init

- **WHEN** DiceBox initializes
- **THEN** the container SHALL have measurable width and height before `box.init()` is called
