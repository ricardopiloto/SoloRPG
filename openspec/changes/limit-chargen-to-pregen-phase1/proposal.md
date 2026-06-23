# Proposal: limit-chargen-to-pregen-phase1

**Data:** 2026-06-22  
**Status:** Draft  
**Relacionado:** `add-user-auth` (personagem starter no cadastro), `add-wfrp-character-creation-flow` (wizard já implementado, adiado na UI), `add-wfrp-solo-mvp` (pregens existentes)

---

## Why

Na primeira fase com autenticação, o objetivo é colocar o jogador no jogo o mais rápido possível: conta verificada → personagem starter automático → campanha. O wizard completo de criação WFRP4e aumenta fricção, superfície de bugs e tempo de validação antes do deploy público.

O motor de criação customizada **permanece no código** (starter aleatório no backend e testes), mas a **UI e os endpoints públicos de wizard** ficam desabilitados até uma fase posterior.

---

## What Changes

### Escopo da fase 1

| Caminho | Fase 1 |
|---------|--------|
| Personagem starter no cadastro (`add-user-auth`) | ✓ Ativo |
| Seleção de pré-gerados (`GET/POST /characters/pregen`) | ✓ Ativo |
| Wizard multi-step em `/character` | ✗ Oculto |
| Endpoints de criação custom (`POST /characters`, validate, roll-*, generate-background) | ✗ Bloqueados quando flag desligada |

### Backend

- Config `ENABLE_CUSTOM_CHARGEN` (default `false` em dev/prod na fase 1)
- Dependency ou guard que retorna `403` com mensagem clara nos endpoints de wizard
- Pregens, listagem, starter character e progressão **inalterados**

### Frontend

- `/character` exibe **somente** a grade de pré-gerados (sem abas wizard/pregen)
- Copy PT-BR ajustada (`chargen.pageLead` etc.) para refletir seleção rápida
- Links existentes (home, campanhas, death) continuam apontando para `/character` para escolher pregen ou ver lista

### Relação com `add-user-auth`

- Remove a expectativa de “criar personagens adicionais pelo wizard” na fase 1
- Personagens adicionais na fase 1: **apenas** escolhendo outro template pregen
- Starter + pregens cobrem onboarding e replay após morte

---

## Capabilities

### Modified Capabilities

- `character-management`: criação custom deferida; pregens + starter como únicos caminhos na fase 1
- `web-interface`: página `/character` sem wizard; mensagens alinhadas

---

## Impact

| Área | Alterações |
|------|------------|
| Backend | `config.py`, guard em rotas de wizard, testes de flag |
| Frontend | `character/page.tsx`, i18n `chargen.*`, remover tab wizard |
| Testes | API 403 com flag off; UI sem botão wizard |
| Docs | README nota de fase; `add-user-auth` tasks 7.2 alinhada na apply |

---

## Non-Goals

- Remover código do wizard (`CharacterCreationWizard`, `character_creation.py`)
- Alterar regras WFRP ou templates pregen
- Limitar quantidade de personagens por conta
- Desabilitar progressão ou campanhas

---

## Open Questions (defaults assumidos)

| Questão | Decisão proposta |
|---------|------------------|
| Código HTTP quando wizard bloqueado | `403 Forbidden` com `detail` PT-BR |
| Default da flag | `ENABLE_CUSTOM_CHARGEN=false` |
| Reativação | Set env `true` + redeploy; sem migration |
| Usuário sem personagens vê o quê | Home/campanhas com CTA para `/character` (pregens); após auth, starter já existe |
