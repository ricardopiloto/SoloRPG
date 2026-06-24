# Proposal: fix-audio-mute-routing-regression

**Data:** 2026-06-24  
**Status:** Draft  
**Relacionado:** `preserve-menu-audio-across-routes`, `restrict-menu-audio-out-of-play`, `add-global-audio-mute-button`

---

## Why

A change `preserve-menu-audio-across-routes` introduziu idempotência em `audioManager.play()` e um early-return no `AudioRoutingProvider` para navegação menu→menu. Isso corrigiu o reinício da trilha entre telas de lobby, mas **regrediu o comportamento do botão Silenciar** fora da sessão de jogo.

Sintomas reportados:

1. A **música tema toca a todo momento** — inclusive quando o jogador espera silêncio após mutar, ou em contextos onde o áudio não deveria reiniciar.
2. O **botão Silenciar no lobby** deixa de cumprir a regra original: parar imediatamente qualquer trilha em reprodução e impedir novos starts até o jogador reativar o som.
3. **Faixas sobrepostas** — ao trocar de tela (ex.: personagens → campanhas), uma **nova** trilha inicia **sem parar a anterior**; duas ou mais músicas ficam audíveis ao mesmo tempo.
4. **Silenciar inconsistente entre telas** — o botão funciona em algumas rotas (ex.: login ou sessão) mas em outras (ex.: campanhas, personagens) a música continua ou volta após navegar.

### Regras que DEVEM ser restauradas (inalteradas em intenção)

| # | Regra |
|---|--------|
| 1 | Trilha **menu** (Theme) **não toca** em `/play/...` |
| 2 | Botão **Silenciar** para **toda** música ambiente (`menu` e `tensao`) imediatamente — **em qualquer rota** onde o botão aparece |
| 3 | Ao **entrar** em sessão (`/play/...`), a trilha menu **para** e não reinicia até sair do jogo |
| 4 | **No máximo uma** trilha ambiente audível por vez — nunca sobreposição de `Audio` elements |

A continuidade menu→menu (sem reiniciar do zero) de `preserve-menu-audio-across-routes` **permanece desejada**, mas só quando o áudio **não está silenciado**.

### Causas prováveis da regressão

**A) Condição de corrida em `play()` assíncrono**

`play()` atribui `currentAudio`, aguarda `await audio.play()`, e só então seta `currentCategory`. Se `stop()` ou `setMuted(true)` ocorre durante o `await`, o callback pode ainda completar e marcar `currentCategory = "menu"` — ou deixar um elemento `<audio>` órfão audível.

**B) `AudioRoutingProvider` usa `muted` do React (assíncrono)**

`toggleMute()` atualiza `audioManager` de forma síncrona, mas o provider lê `muted` via `useAudioMute()` (estado React). Entre o clique em Silenciar e o re-render, uma mudança de rota menu→menu pode avaliar `muted === false` (stale) e o early-return de continuidade **não chama `stop()`** — a trilha que deveria ter parado pode continuar ou ser reativada por um `play()` in-flight.

**C) `bindInteractionRetry` no clique do botão Silenciar**

O listener de retry (`NotAllowedError`) escuta `click` global. O clique em Silenciar pode disparar retry de `play("menu")` na mesma interação se `pendingCategory` ainda estiver setado — competindo com `setMuted(true)`.

**D) Elementos `<audio>` órfãos — duplicação ao navegar**

`play()` é assíncrono. Se uma segunda chamada ocorre enquanto `await audio.play()` da primeira ainda não completou:

1. A segunda chamada pode **não** acionar o early-return idempotente (`currentCategory` ainda `null`, `isPlaying()` ainda `false`).
2. `stop()` pausa só `currentAudio` (a instância mais recente), mas a **primeira** promise pode resolver depois e deixar o primeiro elemento **tocando em paralelo** com o segundo.

Resultado: **duas trilhas sobrepostas** ao trocar de tela — exatamente o sintoma reportado.

**E) Mute “funciona numa tela e noutra não”**

O botão (`AudioMuteButton`) chama o mesmo `audioManager.setMuted()` em todas as rotas (login, `AppShell`, sessão). A inconsistência percebida vem do **roteamento**, não de implementações diferentes do botão:

- Em algumas navegações, `AudioRoutingProvider` chama `playMenu()` com `muted` stale (React) **depois** do clique em Silenciar → música reinicia na nova tela.
- O jogador interpreta como “Silenciar não funciona aqui”, quando na verdade o provider **reiniciou** o áudio após o mute.

Correção: guardas síncronas com `audioManager.isMuted()` em **toda** transição de rota; nunca chamar `play()` se mutado.

---

## What Changes

### Fix 1 — Token de geração em `audioManager.play()`

Introduzir contador `playGeneration`. Cada `play()` captura a geração no início; `stop()` e `setMuted(true)` incrementam a geração. Após `await audio.play()`, só commitar `currentCategory` / `currentAudio` se a geração ainda for válida **e** `!isMuted()` **e** (para menu) `!isInGameRoute()`.

### Fix 2 — `stop()` robusto + instância única

`stop()` deve: pausar e descartar `currentAudio`; limpar `currentCategory`; zerar `pendingCategory`; remover listeners de `bindInteractionRetry`; invalidar plays in-flight (incrementar geração). **Qualquer elemento `<audio>` criado por um `play()` obsoleto MUST ser pausado e descartado no commit pós-`await` se a geração expirou** — garantindo no máximo uma trilha audível.

Opcional reforço: manter referência `lastCreatedAudio` e chamar `pause()` + `src=""` em commits abortados.

### Fix 3 — Provider: decisões com estado síncrono

No `AudioRoutingProvider`, usar `audioManager.isMuted()` (síncrono) nas guardas de roteamento, não apenas o `muted` do hook React. O hook continua para UI do botão; o roteamento não pode depender de estado stale.

Reordenar lógica:

```
if (isMuted() || isInGameRoute(path)) { stop(); return; }
if (!isMenuAudioRoute(path)) { stop(); return; }
if (menu→menu continuity && isPlaying(menu)) { return; }  // só se não mutado
playMenu();
```

### Fix 4 — Mute não reinicia até desmutar explicitamente

`setMuted(false)` **não** inicia áudio sozinho; o `AudioRoutingProvider` chama `playMenu()` quando `muted` passa de `true` → `false` **e** a rota atual é de menu. Garantir que esse path respeita as guardas acima.

### Fix 5 — Testes de regressão

- `setMuted(true)` durante `play()` in-flight → nenhum áudio audível após mute
- **Dois `play("menu")` concorrentes** (segundo antes do `await` do primeiro resolver) → **uma** instância audível
- Lobby: mutar → navegar `/character` → `/campaigns` → silêncio mantido em **ambas** as telas
- Lobby → `/play/` → silêncio; `/play/` → lobby + desmutado → menu inicia uma vez
- Dois `play("menu")` sequenciais em lobby **sem mutar** → continuidade preservada (não regredir `preserve-menu-audio-across-routes`)
- Silenciar em `/campaigns` → navegar para `/character` → **permanece silenciado** (mute global, não por rota)

---

## Capabilities

### Modified Capabilities

- **audio-user-mute** — Silenciar interrompe imediatamente, bloqueia reinício até desmutar, **comportamento idêntico em todas as rotas**
- **audio-routing** — regras 1–4 restauradas; continuidade menu→menu condicionada a `!isMuted()`; **instância única**

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/lib/audio/audioManager.ts` | `playGeneration`; commit pós-await; `stop()` cancela retry |
| `frontend/src/app/providers.tsx` | Guardas com `audioManager.isMuted()` síncrono; continuidade condicionada |
| `frontend/src/lib/audio/audioManager.test.ts` | Testes de mute in-flight, rota `/play/`, continuidade + mute |

---

## Non-Goals

- Slider de volume
- Crossfade entre faixas
- Alterar allowlist de rotas de menu
- Remover continuidade menu→menu (apenas corrigi-la para respeitar mute)

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| `playGeneration` token | Só `flag_modified` / debounce | Token é padrão simples para async cancel |
| `isMuted()` síncrono no provider | Confiar só no React state | Elimina race no clique de Silenciar + navegação; corrige mute “por tela” |
| Abortar `<audio>` órfão no commit | Confiar só em `currentAudio` | `currentAudio` só aponta para o último criado; promises antigas precisam limpar seu próprio elemento |
| Manter early-return menu→menu | Remover e confiar só na idempotência | Menos chamadas; continuidade explícita |

---

## Open Questions

| Questão | Decisão assumida |
|---------|------------------|
| Desmutar em `/play/` inicia menu? | Não — guarda `isInGameRoute` permanece |
| Clique em Silenciar remove `pendingCategory`? | Sim — já feito; reforçar cancelando retry listener |
