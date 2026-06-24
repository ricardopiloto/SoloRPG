# Proposal: preserve-menu-audio-across-routes

**Data:** 2026-06-24  
**Status:** Draft  
**Relacionado:** `add-ambient-audio-engine`, `restrict-menu-audio-out-of-play`, `add-global-audio-mute-button`

---

## Why

A trilha de **menu** (Theme) deve tocar em loop nas telas de meta-jogo (`/character`, `/campaigns`, `/progression`, etc.) e **parar** ao entrar em `/play/...` — esse comportamento está correto hoje.

Porém, ao **navegar entre telas de meta-jogo** (ex.: Personagens → Campanhas), a música **reinicia do zero** (novo elemento `<audio>`, possivelmente outra faixa aleatória). Isso quebra a continuidade ambiente que o jogador espera fora da sessão.

### Causa raiz

1. `AudioRoutingProvider` (`providers.tsx`) executa `playMenu()` em **todo** `pathname` change quando `isMenuAudioRoute(path)` é verdadeiro.
2. `audioManager.play()` **sempre** chama `this.stop()` antes de criar um novo `Audio`, mesmo quando a categoria solicitada já está em reprodução.

```ts
// audioManager.ts — hoje
async play(category) {
  this.stop();           // ← interrompe faixa atual
  const audio = new Audio(randomTrack);
  ...
}
```

Navegação `/character` → `/campaigns` dispara o efeito duas vezes com `playMenu()` → stop + restart.

---

## What Changes

### Fix 1 — `play()` idempotente por categoria

Em `audioManager.ts`, rastrear `currentCategory: AudioCategory | null`. Se `play(category)` for chamado com a **mesma categoria** já em reprodução (elemento ativo, não pausado), retornar sem `stop()` nem novo `Audio`.

Trocar de categoria (`menu` → `tensao` ou vice-versa) continua fazendo `stop()` + novo playback.

### Fix 2 — Roteamento mais enxuto (opcional, recomendado)

Em `AudioRoutingProvider`, chamar `playMenu()` apenas quando:

- entra em rota de menu **vindo de** rota de jogo (`/play/`) ou rota sem áudio; ou
- jogador **desmuta** o áudio estando em rota de menu

Evita chamadas redundantes em cada troca entre rotas allowlisted.

### Fix 3 — Testes

- Unitário: dois `play("menu")` seguidos → um único `Audio` instance, sem segundo `stop`.
- Unitário: `play("menu")` depois `play("tensao")` → substitui (dois elementos ou stop explícito).
- Unitário / integração leve: simular transição de pathname `/character` → `/campaigns` → menu não reinicia.

---

## Capabilities

### Modified Capabilities

- **audio-routing** — continuidade da trilha menu entre rotas de meta-jogo; parada ao entrar em `/play/` inalterada

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/lib/audio/audioManager.ts` | `currentCategory`; early-return em `play()` |
| `frontend/src/app/providers.tsx` | Lógica de transição de rota (evitar `playMenu` redundante) |
| `frontend/src/lib/audio/audioManager.test.ts` | Novos casos de idempotência e troca de categoria |

---

## Non-Goals

- Crossfade entre faixas Theme 1 / Theme 2 ao navegar (continua a faixa já sorteada na sessão de lobby)
- Retomar posição exata do MP3 após refresh da página (novo load = novo start, aceitável)
- Alterar comportamento de tensão in-game (`scene_mood`)
- Alterar allowlist de rotas de menu

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| Idempotência em `audioManager.play()` | Só otimizar `AudioRoutingProvider` | Protege qualquer callsite futuro; defesa em profundidade |
| Manter sorteio aleatório só no primeiro `play("menu")` | Re-sortear a cada rota | Usuário pediu continuidade, não variedade |
| `currentCategory` em memória do singleton | Persistir faixa em `sessionStorage` | Escopo mínimo; refresh reiniciando é aceitável |

---

## Open Questions

| Questão | Decisão assumida |
|---------|------------------|
| Sair de `/play/` para `/campaigns` deve iniciar menu do zero? | Sim — sessão tinha parado o menu; primeiro `play("menu")` após saída é esperado |
| Desmutar em `/character` com menu já tocando? | Não reiniciar se já estiver tocando (idempotência) |
| Rota allowlist → rota allowlist com menu pausado por `NotAllowedError`? | Segundo `play("menu")` na mesma categoria retenta se ainda pendente; não duplicar elemento |
