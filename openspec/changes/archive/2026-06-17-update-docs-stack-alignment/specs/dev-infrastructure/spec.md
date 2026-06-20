## ADDED Requirements

### Requirement: Documentation Stack Alignment
Project documentation in `Docs/` SHALL reflect the implemented technology stack: FastAPI/Python backend, Next.js frontend, DeepSeek as default LLM provider, and Open Design prototype as UI reference.

#### Scenario: Developer reads technical research
- **WHEN** a developer opens `Docs/technical-research.md`
- **THEN** the architecture diagram shows FastAPI backend
- **AND** the LLM section documents the model-agnostic adapter with DeepSeek as implementation default

#### Scenario: Developer finds UI reference
- **WHEN** a developer opens `Docs/README.md`
- **THEN** they find links to ux-spec, prototype gap analysis, and Open Design project path
- **AND** the development order references `add-frontend-prototype-parity` instead of superseded proposals
