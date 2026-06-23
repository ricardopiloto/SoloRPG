# Design: limit-chargen-to-pregen-phase1

## Context

**Estado atual**

- Wizard WFRP4e completo em `/character` com abas **Pré-gerados** e **Criar personagem** (`CharacterCreationWizard`).
- Backend expõe endpoints de preview/validação/persistência custom (`POST /characters`, `/characters/validate-creation`, rolls, `generate-background`).
- Pregens funcionam via `GET/POST /characters/pregen`.
- `add-user-auth` (em draft) prevê personagem starter aleatório no verify; também menciona wizard para personagens extras.

**Motivação**

Reduzir escopo da primeira entrega autenticada: menos telas, menos endpoints expostos, onboarding mais curto. O wizard volta na fase 2 sem reimplementação.

---

## Goals / Non-Goals

**Goals**

- Ocultar wizard na UI.
- Bloquear endpoints custom quando `ENABLE_CUSTOM_CHARGEN=false`.
- Manter pregens, starter (auth) e fluxos de campanha/sessão.
- Feature flag simples para reativar wizard depois.

**Non-Goals**

- Deletar componentes ou motor de regras.
- Feature flags granulares por usuário ou A/B.
- Novo fluxo de “reroll starter”.

---

## Decisions

### 1. Feature flag central

```python
# backend/app/config.py
enable_custom_chargen: bool = False  # env ENABLE_CUSTOM_CHARGEN
```

**Decisão:** uma flag booleana; default `false` na fase 1.

**Alternativa rejeitada:** só esconder no frontend — cliente autenticado ainda poderia chamar a API.

### 2. Guard de API

Dependency `require_custom_chargen_enabled` aplicada a:

- `POST /characters` (body wizard)
- `POST /characters/validate-creation`
- `POST /characters/creation/roll-*`
- `POST /characters/generate-background`

Resposta: `403` com corpo `{"detail": "Criação customizada indisponível nesta fase."}` (ou chave i18n no frontend se mapeada).

**Não bloquear:**

- `GET/POST /characters/pregen`
- `GET /characters`, `GET /characters/{id}`
- Progressão
- Geração interna de starter (`starter_character.py`) — server-side, não passa pelo guard público

### 3. Frontend `/character`

**Decisão:** remover tabs e renderizar só a grade de pregens.

```tsx
// Antes: mode "pregen" | "wizard" com tab buttons
// Depois: lista pregens direto; CharacterCreationWizard não importado quando flag off
```

**Implementação:** ler flag via env público Next `NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN` (default false) **ou** inferir indisponibilidade após 403 no primeiro load — preferir env espelhando backend para evitar flash de UI.

**Alternativa rejeitada:** manter tab desabilitada com tooltip — ainda confunde; esconder completamente.

### 4. Copy e navegação

- `chargen.pageLead`: texto sobre escolher um arquetipo pré-gerado para começar.
- Remover/ocultar chaves `chargen.wizardTab` da UI (podem permanecer no JSON para fase 2).
- Home pós-login (`add-user-auth`): destaque ao starter existente; link “Outro personagem” → `/character` (pregens).

### 5. Sequenciamento com `add-user-auth`

| Task add-user-auth | Ajuste na apply |
|--------------------|-----------------|
| 7.2 wizard + pregens exigem login | Apenas pregens + listagem; wizard fora |
| 4.3 wizard exige user_id | Guard de flag antes de ownership |

Aplicar **`limit-chargen-to-pregen-phase1` junto ou imediatamente após** `add-user-auth`.

---

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Jogador quer customizar atributos | Pregens variados; fase 2 reativa wizard |
| Divergência FE/BE flags | Documentar par `ENABLE_CUSTOM_CHARGEN` + `NEXT_PUBLIC_*` |
| Testes do wizard quebram | Testes de wizard rodam com flag `true` em fixture dedicada |

---

## Migration Plan

1. Deploy backend com flag default `false`.
2. Deploy frontend sem wizard.
3. Fase 2: set `ENABLE_CUSTOM_CHARGEN=true`, redeploy FE com flag true, reexibir aba wizard.

Sem migration de banco.

---

## Open Questions

Nenhuma bloqueante — defaults na proposal.
