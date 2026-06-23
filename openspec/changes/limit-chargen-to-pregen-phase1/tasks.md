# Tasks: limit-chargen-to-pregen-phase1

## 1. Backend feature flag

- [x] 1.1 Adicionar `enable_custom_chargen: bool = False` em `config.py` (`ENABLE_CUSTOM_CHARGEN`)
- [x] 1.2 Documentar par de envs em `.env.example` e README

## 2. API guard

- [x] 2.1 Criar `require_custom_chargen_enabled` em `deps.py` (403 PT-BR quando false)
- [x] 2.2 Aplicar guard em `POST /characters` (wizard), validate-creation, roll-*, generate-background
- [x] 2.3 Confirmar pregens e starter interno **sem** guard
- [x] 2.4 Testes: endpoints wizard → 403 com flag off; pregens → 200

## 3. Frontend `/character`

- [x] 3.1 Adicionar `NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN` (default false)
- [x] 3.2 Remover tabs wizard/pregen quando flag off; exibir só grade de pregens
- [x] 3.3 Lazy/import condicional de `CharacterCreationWizard` apenas quando flag on
- [x] 3.4 Atualizar `chargen.pageLead` e textos relacionados em `pt-BR.json`

## 4. Integração auth (apply conjunta)

- [x] 4.1 Alinhar task 7.2 de `add-user-auth`: login + pregens, sem wizard
- [x] 4.2 Home pós-login: CTA coerente (starter já presente; link para pregen se quiser outro)

## 5. Validação

- [x] 5.1 `pytest` verde (incl. testes wizard com flag on em fixture)
- [x] 5.2 `npm run build` verde
- [x] 5.3 Manual: `/character` só pregens; tentativa API wizard → 403; pregen OK
