# Proposal: restrict-menu-audio-out-of-play

**Data:** 2026-06-23  
**Status:** Draft  
**Relacionado:** `add-ambient-audio-engine`  
**Design:** `design.md`

---

## Why

A trilha de **menu** (Theme) deve ambientar apenas as telas de meta-jogo — personagens, campanhas, encerramento de sessão, login, etc. Na **tela de jogo** (`/play/...`), essa música não deve tocar: o jogador precisa de silêncio (ou, no máximo, a trilha de tensão disparada pelo GM via `[MUSICA]` durante cenas específicas).

O `AudioRoutingProvider` atual usa uma regra negativa (`pathname` **não** começa com `/play/` → `playMenu()`). Isso é frágil:

- Qualquer rota nova fora do escopo pretendido (ex.: `/landing`, `/`) pode tocar menu sem intenção explícita
- Não há guarda centralizada impedindo que `play("menu")` rode enquanto o jogador está em sessão
- A intenção de produto (“só fora de jogo”) não está codificada como allowlist documentada

Esta change torna o roteamento **explícito e à prova de regressão**.

---

## Comportamento desejado

| Contexto | Trilha menu (Theme) | Trilha tensão (`[MUSICA]`) |
|----------|---------------------|----------------------------|
| Login, personagem, campanhas, home, progressão, fim/morte de sessão | ✅ Toca (loop, volume baixo) | ❌ Não toca |
| Tela de jogo `/play/[sessionId]` | ❌ **Para imediatamente** | ✅ Só se GM emitir `mood: "tensão"` e áudio **não** estiver silenciado |
| Jogador ativou **Silenciar** (qualquer tela) | ❌ Não toca | ❌ Não toca |
| Logout | ❌ Para | ❌ Para |

Ao **entrar** em `/play/...`: stop imediato da trilha menu.  
Ao **sair** de `/play/...` para rota permitida: retoma trilha menu.

---

## What Changes

### 1. Allowlist de rotas para trilha menu

Novo módulo `frontend/src/lib/audio/audioRoutes.ts` (ou equivalente) com:

- `isInGameRoute(pathname)` → `true` se `pathname.startsWith("/play/")`
- `isMenuAudioRoute(pathname)` → `true` apenas para rotas de meta-jogo explícitas

Rotas permitidas (inicial):

| Rota | Tela |
|------|------|
| `/` | Home / dashboard |
| `/login` | Login |
| `/register` | Cadastro (fase 2) |
| `/verify-email` | Verificação |
| `/character` | Personagens |
| `/campaigns` | Campanhas |
| `/progression` | Progressão |
| `/session/end` | Encerramento de sessão |
| `/session/death` | Morte do personagem |
| `/landing` | Landing pública (se usada) |

Qualquer outra rota → **sem** trilha menu (silêncio).

### 2. `AudioRoutingProvider` — allowlist em vez de denylist

Em `providers.tsx`:

- Se `isInGameRoute(pathname)` → `stop()` (nunca `playMenu`)
- Senão, se `isMenuAudioRoute(pathname)` → `playMenu()`
- Senão → `stop()`

### 3. Guarda no `audioManager`

Em `audioManager.play(category)`:

- Se `category === "menu"` e `isInGameRoute(window.location.pathname)` → **no-op** (não inicia)
- Evita race conditions se outro código chamar `play("menu")` durante sessão

### 4. Guarda no `setMood` / tensão

Em `useAudioPlayer.setMood`:

- `tensão` → só chama `play("tensao")` se `isInGameRoute(pathname)`; caso contrário ignora
- `normal` → `stop()` (válido em qualquer contexto)

`useSessionPlay` continua chamando `setMood(scene_mood)` — a guarda fica no hook.

### 5. Controle **Silenciar** do jogador

Botão no header da tela de jogo (`play/[sessionId]/page.tsx`), **ao lado de** `⏸ Pausar`:

- Rótulo: `🔇 Silenciar` quando áudio ativo; `🔊 Ativar som` quando silenciado (ou ícone equivalente)
- `title` acessível: "Desativar toda a música ambiente" / "Reativar música ambiente"
- Estilo visual alinhado ao botão Pausar (mesma linha, `text-xs`, borda)

Estado **global** persistido em `localStorage` (ex.: `wfrp-audio-muted`):

- `true` → `audioManager.play()` é no-op para qualquer categoria; `stop()` imediato ao silenciar
- `false` → roteamento normal (allowlist + `scene_mood`)
- Preferência sobrevive refresh e navegação entre rotas até o jogador reativar

Implementação sugerida:

- `audioManager.setMuted(boolean)` + `isMuted()` — fonte de verdade em memória, sync com `localStorage`
- `AudioRoutingProvider` e `setMood` consultam `isMuted()` antes de iniciar playback
- Ao **silenciar**: `stop()` + `setMuted(true)`
- Ao **reativar**: `setMuted(false)` + reavalia rota atual (menu em allowlist, tensão não retoma automaticamente sem novo `scene_mood`)

### 6. Documentação

Atualizar `add-ambient-audio-engine/design.md` (ou referência cruzada) com a allowlist como fonte de verdade.

---

## Capabilities

### Modified Capabilities

- **audio-routing**: trilha menu restrita a rotas de meta-jogo; tela de jogo sempre sem menu theme
- **audio-user-mute**: preferência global do jogador para silenciar todo áudio ambiente

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/lib/audio/audioRoutes.ts` | Novo — helpers de rota |
| `frontend/src/lib/audio/audioManager.ts` | Guarda `play("menu")` em rota de jogo |
| `frontend/src/app/providers.tsx` | Allowlist no `AudioRoutingProvider` |
| `frontend/src/hooks/useAudioPlayer.ts` | `setMood` ciente de rota (`usePathname`) + `isMuted` |
| `frontend/src/app/play/[sessionId]/page.tsx` | Botão Silenciar / Ativar som ao lado de Pausar |
| `frontend/src/messages/pt-BR.json` | Chaves i18n `session.muteAudio` / `session.unmuteAudio` |
| `openspec/changes/add-ambient-audio-engine/design.md` | Nota de supersede parcial do routing |

---

## Non-Goals

- Slider de volume contínuo (só mute on/off)
- Crossfade entre tracks
- Servir áudio pelo backend (continua estático em `public/audio/`)
- Remover sinal `[MUSICA]` ou trilha de tensão in-game (continua disponível quando som ativo)
- Tocar menu theme em rotas não listadas “por conveniência”
- Botão de mute em todas as telas do app (MVP: header da sessão `/play/` apenas; estado global afeta todas as rotas)

---

## Open Questions

| Questão | Decisão assumida |
|---------|------------------|
| Home `/` deve tocar menu? | Sim — dashboard pós-login é meta-jogo |
| `/landing` deve tocar menu? | Sim, se rota existir; caso contrário omitir da allowlist |
| Tensão via `[MUSICA]` na sessão? | Mantida — é música de cena, não menu; só toca em `/play/` e com som ativo |
| Mute persiste entre sessões? | Sim — `localStorage`; jogador reativa manualmente |
| Ao reativar som em `/play/` sem novo `scene_mood`? | Silêncio in-game até GM emitir tensão ou jogador sair para rota com menu |
| Testes automatizados de rota? | Unit tests em `audioRoutes.ts`; E2E manual opcional |
