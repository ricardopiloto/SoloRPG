## ADDED Requirements

### Requirement: UI MUST show fortune re-roll prompt on failed test

After a failed GM-requested test, the UI SHALL offer at most one Fortune re-roll while `fortune_reroll_available` is true.

- **WHEN** a GM-requested test fails and the character has Fortune Points remaining **and** Fortune has not yet been spent on that test instance (`fortune_reroll_available = true`)
- **THEN** the UI SHALL offer an option to spend a Fortune Point to re-roll once
- **AND** SHALL NOT offer a +10 bonus alternative

#### Scenario: No prompt after fortune already used on test

- **WHEN** the player failed a test, spent Fortune to re-roll once, and failed again
- **THEN** the UI SHALL NOT show the Fortune re-roll button again for that test
- **AND** SHALL show only the option to continue with the failed result
