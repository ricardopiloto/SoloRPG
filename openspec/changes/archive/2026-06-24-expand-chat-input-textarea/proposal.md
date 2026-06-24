# Proposal: expand-chat-input-textarea

**Data:** 2026-06-23  
**Status:** Draft  
**Arquivo afetado:** `frontend/src/app/play/[sessionId]/page.tsx` (principal) + `globals.css` (mínimo)

---

## Why

O campo de texto para a ação do jogador é atualmente um `<input type="text">` de linha única. Ao digitar textos longos (ações detalhadas, diálogos, descrições), o texto some para a direita da tela — o jogador não consegue rever o que escreveu antes de enviar, nem corrigir partes do meio.

A solução é substituir o `<input>` por um `<textarea>` que **cresce verticalmente** conforme o conteúdo, mantendo todo o texto sempre visível. Não é uma mudança de funcionalidade — o texto enviado continua sendo texto normal, sem quebras de linha literais. O comportamento de submit (Enter = enviar) é preservado.

---

## What Changes

### 1. `<input>` → `<textarea>` auto-crescente

Em `play/[sessionId]/page.tsx`, o `<input name="action">` é substituído por `<textarea name="action">` com:

- `rows={1}` — começa com 1 linha de altura
- `resize: none` — sem handle de resize manual (não é um editor de texto)
- Auto-crescimento via `field-sizing: content` (CSS moderno, suportado por todos os browsers alvo) **ou** handler `onInput` que ajusta `scrollHeight` (fallback compatível)
- `max-height` limitado (ex: `8rem` / ~4 linhas) — não domina a tela em textos muito longos, adiciona scroll vertical interno após esse limite
- `overflow-y: auto` acima do `max-height`

### 2. Comportamento de teclado

- **Enter** → submit (preserva comportamento atual)
- **Shift+Enter** → nova linha literal (opcional, mas natural para textarea)

O handler `onKeyDown` substitui o submit via Enter padrão do form:

```
onKeyDown: se Enter sem Shift → prevenir default + submit
```

### 3. Submit via form

O `onSubmit` do form atual usa `elements.namedItem("action") as HTMLInputElement`. A conversão exige cast para `HTMLTextAreaElement` (propriedade `.value` é idêntica).

### 4. Reset após envio

Atualmente `input.value = ""` — com textarea: `textarea.value = ""` + reset da altura para `auto` ou `1 row` para voltar à altura mínima.

---

## Capabilities

### Modified Capabilities

- **chat-input-ux**: campo de ação do jogador cresce verticalmente com o conteúdo em vez de rolar horizontalmente

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/app/play/[sessionId]/page.tsx` | `<input>` → `<textarea>` com handler de teclado; cast HTMLTextAreaElement |
| `frontend/src/app/globals.css` | Estilo `.chat-input-textarea` com `resize: none`, `max-height`, `overflow-y` |

---

## Non-Goals

- Enviar quebras de linha literais para o backend (o texto enviado é uma linha contínua, ou a action do jogador com `\n` se Shift+Enter for usado — o backend já aceita texto livre)
- Markdown ou formatação dentro do campo
- Histórico de input (seta para cima para revisitar ações anteriores) — escopo separado
- Mobile virtual keyboard behavior — fora de escopo do MVP

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| `field-sizing: content` via CSS | JS `onInput` + scrollHeight | Mais simples; browsers alvo (Chrome 123+, Firefox 128+) suportam; sem JS extra |
| `max-height: 8rem` com `overflow-y: auto` | Sem limite (cresce infinito) | Evita que a área de chat encolha demais em textos muito longos |
| Enter = submit, Shift+Enter = nova linha | Enter = nova linha, botão = submit | Preserva o hábito do jogador atual; Shift+Enter é padrão de apps de mensagem |
