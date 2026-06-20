# Proposal: update-session-pausable-ux

**Data:** 2026-06-16  
**Status:** Draft  
**Escopo:** `frontend/messages/pt-BR.json` · `frontend/src/app/play/[sessionId]/page.tsx` · `openspec/project.md` · `README.md` · `Docs/product-brief.md` · `Docs/mvp-validation-checklist.md`

---

## Contexto

A change `add-session-pause-resume` (arquivada) implementou pausa e retomada de sessão com sucesso:
- Botão "⏸ Pausar" no header da sessão
- API `/sessions/{id}/pause` e `/sessions/{id}/resume`
- Auto-resume ao re-entrar na sessão pausada
- Tela de campanhas exibe "Retomar sessão" para sessões pausadas

Porém, múltiplos textos no frontend e nos documentos continuam afirmando que sessões **não são pausáveis** — informação incorreta que pode confundir o jogador.

---

## Problemas identificados

### 1. Hint no input da sessão — `session.notPausable`

`page.tsx:150`:
```tsx
{awaitingRoll ? t("session.pendingTest") : t("session.notPausable")}
```

Exibe "Sessão não pausável." abaixo do campo de ação durante o jogo. É uma informação errada — a sessão pode ser pausada com o botão "⏸ Pausar" já visível no header.

**Solução:** Remover o hint de texto abaixo do input quando não há teste pendente, ou substituir por uma dica neutra sobre o botão de pausa no header.

### 2. Overlay de início de sessão — `session.prepareBody`

`pt-BR.json:29`:
```json
"prepareBody": "Duração estimada: ~{minutes} minutos. A sessão não pode ser pausada."
```

A frase "A sessão não pode ser pausada." aparece no modal antes de iniciar a sessão. É incorreta.

**Solução:** Remover a frase. O novo texto: `"Duração estimada: ~{minutes} minutos. Você pode pausar e retomar quando quiser."`.

### 3. `openspec/project.md` — constraint desatualizado

Linha 51: `Sessions are non-pausable; duration announced before start`

**Solução:** Atualizar para `Sessions are pausable; player can pause and resume at any time. Duration is announced before start.`

### 4. `README.md` — feature list desatualizada

Linha 137: `Jogar sessão via texto livre (timer visível, não pausável)`

**Solução:** Atualizar para `Jogar sessão via texto livre (timer visível, pausável)`

### 5. `Docs/product-brief.md` e `Docs/mvp-validation-checklist.md`

Docs históricos que mencionam "sessões não pausáveis". Atualizar para refletir a implementação real.

---

## Solução resumida

| Arquivo | Mudança |
|---|---|
| `pt-BR.json` | `notPausable` → `pauseHint`: `"Use ⏸ no topo para pausar."` |
| `pt-BR.json` | `prepareBody`: remover "não pode ser pausada", adicionar "pode pausar e retomar" |
| `page.tsx` | Usar nova chave `session.pauseHint` (ou remover hint por completo) |
| `openspec/project.md` | Atualizar constraint de sessão |
| `README.md` | Atualizar linha da feature |
| `Docs/product-brief.md` | Atualizar bullet sobre pausabilidade |
| `Docs/mvp-validation-checklist.md` | Atualizar checklist item |

---

## Não-escopo

- Alterações no backend (pausa/resume já implementados e funcionando)
- Redesign do botão "⏸ Pausar" (já existe e funciona)
- Tela de campanhas (já exibe "Retomar sessão" corretamente)
