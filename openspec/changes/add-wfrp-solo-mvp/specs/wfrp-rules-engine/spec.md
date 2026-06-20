## ADDED Requirements

### Requirement: Server-Side Dice Rolling
The system SHALL roll all dice server-side. The LLM SHALL NOT roll dice or determine mechanical outcomes. The player SHALL see dice roll animation and result in the UI before the GM narrates the consequence.

#### Scenario: Attribute test roll
- **WHEN** the backend receives a `[TESTE]` signal with tipo "teste_atributo"
- **THEN** the system rolls d100 server-side
- **AND** compares against the character's attribute (plus skill advances and situational modifier)
- **AND** sends the roll result to the UI for animation display
- **AND** sends the formatted result to the LLM for narration (e.g., "Teste de Agilidade: rolou 34, atributo 45 — SUCESSO por 1 nível")

#### Scenario: Player cannot manipulate rolls
- **WHEN** a player inspects network requests or UI
- **THEN** no client-side mechanism exists to set or alter dice results

### Requirement: Attribute and Skill Tests
The system SHALL resolve WFRP4e d100 tests with success/failure levels based on roll vs. target (attribute + skill advances + modifiers).

#### Scenario: Successful skill test with margin
- **WHEN** a test roll is below or equal to the target value
- **THEN** the system calculates success level by margin of success
- **AND** returns the level to the LLM for narrative consequence

#### Scenario: Failed skill test
- **WHEN** a test roll exceeds the target value
- **THEN** the system calculates failure level
- **AND** returns failure details for LLM narration of consequencia_falha

### Requirement: Melee and Ranged Combat Resolution
The system SHALL resolve melee attacks (tipo "ataque_cc") using Weapon Skill and Strength, and ranged attacks (tipo "ataque_distancia") using Ballistic Skill with range modifiers (curto/medio/longo/extremo).

#### Scenario: Melee attack hit
- **WHEN** a melee attack test succeeds
- **THEN** the system calculates damage as Strength + success margin minus target Damage Reduction
- **AND** applies wounds to the target
- **AND** returns combat state to the LLM

#### Scenario: Ranged attack at long range
- **WHEN** a ranged attack is declared with alcance "longo"
- **THEN** the system applies the appropriate range modifier to the Ballistic Skill test
- **AND** resolves hit/miss and damage server-side

### Requirement: Critical Hits and Wounds
The system SHALL use d10 for wound application. When wounds reach 0, the system SHALL roll Critical Hit tables server-side and return results to the LLM.

#### Scenario: Wounds reduced to zero
- **WHEN** an attack reduces a character's wounds to 0
- **THEN** the system rolls on the Critical Hit table
- **AND** returns critical severity and effect to the LLM for narration
- **AND** does NOT delegate critical resolution to the LLM

### Requirement: Fate and Fortune Points
The system SHALL track Fate Points and Fortune Points on the character sheet. When a lethal critical occurs, the system SHALL offer Fate Point expenditure if available. Without Fate Points, death is permanent.

#### Scenario: Lethal critical with Fate Point available
- **WHEN** the GM emits `[ACAO_SISTEMA]` tipo "usar_ponto_destino"
- **AND** the character has Fate Points remaining
- **THEN** the system deducts one Fate Point
- **AND** sets wounds to 1 and ignores the critical effect
- **AND** updates character state

#### Scenario: Lethal critical without Fate Points
- **WHEN** a lethal critical occurs and the character has zero Fate Points
- **THEN** the system processes `[ACAO_SISTEMA]` tipo "morte_personagem"
- **AND** marks the character as dead
- **AND** marks the campaign as unfinished (inacabada)

### Requirement: XP Validation and Award
The system SHALL validate XP suggested by the LLM in `[FIM_SESSAO]` resumo_sistema.xp_sugerido, accepting values between 30 and 100 per session, and award XP to the character upon session end.

#### Scenario: Valid XP at session end
- **WHEN** session ends with xp_sugerido of 50
- **THEN** the system adds 50 XP to the character's total
- **AND** persists the award with the session record

#### Scenario: XP outside valid range
- **WHEN** session ends with xp_sugerido outside 30–100
- **THEN** the system clamps or rejects the value per validation rules
- **AND** logs the adjustment

### Requirement: Career Progression Rules
The system SHALL implement WFRP4e career advances: skill advances, talent purchases, and career tier progression within WFRP4e rules. Progression between sessions SHALL occur without LLM involvement.

#### Scenario: Player buys skill advance between sessions
- **WHEN** the player spends XP on a valid skill advance during the progression screen
- **THEN** the system deducts XP per WFRP4e cost tables
- **AND** updates the character's skill advances
- **AND** persists the change before the next session

### Requirement: Insanity and Corruption Excluded
The system SHALL NOT implement WFRP4e Insanity or Corruption mechanics in the MVP.

#### Scenario: Narrative chaos exposure
- **WHEN** the character encounters corruption-themed narrative events
- **THEN** the system tracks narrative consequences only (karma/reputation)
- **AND** does NOT apply Insanity or Corruption point mechanics
