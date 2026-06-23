## ADDED Requirements

### Requirement: WFRP4e character creation rules engine
The backend SHALL implement deterministic WFRP4e Core character creation rules including species options, career selection, characteristic generation (roll or point-buy), skill and talent allocation, trapping assignment, derived stat calculation, and creation XP accounting.

#### Scenario: Roll characteristics for Human
- **WHEN** the player chooses rolled characteristics for a Human character
- **THEN** the backend generates ten values using `2d10+20` per attribute
- **AND** allows exactly one optional full reroll and any number of pairwise swaps before finalizing
- **AND** awards creation XP per rulebook/Foundry parity (50 for first roll, 25 if swapped without reroll, 0 after reroll)

#### Scenario: Point-buy characteristics
- **WHEN** the player chooses point-buy instead of rolling
- **THEN** the backend validates 100 points spent across attributes with each allocated value between 4 and 18 before species bonus
- **AND** awards 0 creation XP from the characteristics step

#### Scenario: Derived wounds and fate
- **WHEN** a creation draft is finalized with valid attributes
- **THEN** `wounds_max` is computed as Strength Bonus + Toughness Bonus (minimum 1)
- **AND** `fate_max` is computed from species base plus allotted fate points from the species extra pool
- **AND** the client cannot override these values directly

#### Scenario: Career skill allocation
- **WHEN** the player allocates career skill advances during creation
- **THEN** the backend enforces a maximum of 40 total points across career skills
- **AND** enforces a maximum of 10 advances per individual career skill

#### Scenario: Reject invalid creation draft
- **WHEN** a creation draft violates any creation rule (e.g., exceeds skill point budget, invalid attribute allocation, missing career talent choice)
- **THEN** `POST /characters/validate-creation` returns `valid: false` with step-scoped error messages
- **AND** `POST /characters` rejects the same payload with HTTP 422

### Requirement: Core career catalog for creation
The system SHALL provide a static Tier 1 career catalog from the WFRP4e Core Rulebook (Portuguese names) including career skills, talent options, trappings, and Human career roll table weights.

#### Scenario: List Tier 1 careers
- **WHEN** the client requests `GET /rules/careers?tier=1`
- **THEN** the response includes all Core Tier 1 careers available for creation
- **AND** each entry includes `id`, `name`, `career_group`, and `class`

#### Scenario: Career detail for wizard
- **WHEN** the client requests `GET /rules/careers/{id}` for a valid Tier 1 career
- **THEN** the response includes skills list, talent options, and starting trappings needed by the creation wizard

#### Scenario: Roll Human career table
- **WHEN** the player chooses to roll for a career during creation
- **THEN** the backend selects a Tier 1 career using the Human Reikland d100 table
- **AND** awards creation XP per step rules (50 first roll, 25 on second batch of two rolls, 0 thereafter)

### Requirement: Creation XP accounting
The system SHALL track XP gained from random choices during creation separately from XP spent on creation advances, persisting the resulting `xp_total` and `xp_spent` on the new character.

#### Scenario: XP from rolled species and career
- **WHEN** the player rolls species (+20 XP) and rolls career once (+50 XP) and rolls characteristics (+50 XP)
- **THEN** the character starts with `xp_total` of 120 minus any XP spent on attribute advances during creation
- **AND** `xp_spent` reflects advances purchased at creation

## MODIFIED Requirements

### Requirement: Custom Character Creation
The player SHALL create a custom character through a guided multi-step wizard that enforces WFRP4e Core creation rules server-side. Free-form attribute, wounds, and fate entry SHALL NOT be accepted.

#### Scenario: Guided custom character creation flow
- **WHEN** the player chooses custom creation
- **THEN** the system presents the steps: Species → Career → Attributes → Skills & Talents → Trappings review → Details
- **AND** validates each step via the backend rules engine
- **AND** persists a rules-valid character before campaign start

#### Scenario: Legacy free-form creation rejected
- **WHEN** the client submits a legacy free-form `CharacterCreate` payload without a validated creation draft
- **THEN** the API returns HTTP 422
- **AND** does not persist the character

#### Scenario: Pre-generated path unchanged
- **WHEN** the player selects a pre-generated template
- **THEN** the existing pregen flow continues to work without the wizard

### Requirement: AI-generated character background
During the Details step of character creation, the system SHALL offer optional AI-assisted background generation using the application's configured LLM adapter with a dedicated non-GM system prompt for WFRP4e character backstory.

#### Scenario: Generate background from creation draft
- **WHEN** the player clicks "Gerar com IA" on the Details step with a valid draft (at minimum name and career)
- **THEN** the backend calls the LLM with `Docs/character-background-prompt.md` as system prompt (not the GM prompt)
- **AND** returns a PT-BR background text informed by species, career, talents, and optional player hints
- **AND** does not modify any mechanical character fields

#### Scenario: Player edits generated background
- **WHEN** the backend returns a generated background
- **THEN** the UI populates the background textarea
- **AND** the player can edit or regenerate before final character submission

#### Scenario: LLM failure during background generation
- **WHEN** the LLM call fails or times out
- **THEN** the API returns an error with a user-visible message
- **AND** the player can still enter background text manually

#### Scenario: Mock provider for tests
- **WHEN** `LLM_PROVIDER=mock` and the client requests background generation
- **THEN** the backend returns deterministic mock background text without external network calls
