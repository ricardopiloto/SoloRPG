## MODIFIED Requirements

### Requirement: End-to-End Game Loop Test
The project SHALL include an E2E test covering: authenticate → select pre-generated character → start campaign → session turn → progression screen. The test SHALL authenticate before accessing protected routes.

#### Scenario: Playwright E2E passes with auth
- **WHEN** E2E test runs against local stack
- **THEN** the test establishes an authenticated session before visiting `/character`
- **AND** the main game loop completes without errors

#### Scenario: E2E fails fast without auth
- **WHEN** E2E attempts to access `/character` without authentication
- **THEN** the test does not proceed with the game loop (redirect to login is expected)
