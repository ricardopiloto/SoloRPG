# Proposal: add-global-audio-mute-button

**Data:** 2026-06-24  
**Status:** Draft  
**Relacionado:** `restrict-menu-audio-out-of-play` (arquivada), `add-ambient-audio-engine` (arquivada)

---

## Why

O controle **Silenciar / Ativar som** foi implementado apenas no header da sessão (`/play/[sessionId]`), ao lado de **Pausar**. Fora do jogo — campanhas, personagens, home, encerramento de sessão — a trilha menu pode estar tocando, mas o jogador **não tem como silenciar** sem entrar numa sessão primeiro.

A preferência de mute já é global (`localStorage` + `audioManager`), mas a UI não acompanha. O jogador precisa do mesmo botão nas telas de meta-jogo.

---

## Comportamento atual vs desejado

| Tela | Música menu possível | Botão Silenciar hoje |
|------|----------------------|----------------------|
| `/play/...` | Não (só tensão via GM) | ✅ Sim |
| `/`, `/character`, `/campaigns`, etc. (AppShell) | Sim | ❌ Não |
| `/login` | Sim | ❌ Não |

**Desejado:** botão visível em **todas** as telas fora de `/play/...` onde o usuário autenticado navega, **e** manter o botão na sessão de jogo.

---

## What Changes

### 1. Componente reutilizável `AudioMuteButton`

Novo `frontend/src/components/audio/AudioMuteButton.tsx`:

- Usa `useAudioMute()` (`muted`, `toggleMute`)
- Mesmo visual do botão atual na sessão (`text-xs`, borda, hover)
- Props opcionais: `className`, `size` (`sm` default) para encaixar no `AppShell` e no `game-header`
- `title` e label via i18n

### 2. `AppShell` — botão no topnav

Em `frontend/src/components/layout/AppShell.tsx`, na área direita do header (antes de logout / nova campanha):

- Renderizar `<AudioMuteButton />` quando `user` estiver autenticado
- Cobre: `/`, `/character`, `/campaigns`, `/progression`, `/session/end`, `/session/death`

### 3. Login — botão discreto

Em `frontend/src/app/login/page.tsx`:

- Botão no canto superior direito (ou abaixo do logo), pois `/login` está na allowlist de menu audio e não usa `AppShell`

### 4. Sessão — refatorar para o componente

Em `play/[sessionId]/page.tsx`:

- Substituir markup inline do botão por `<AudioMuteButton />` (comportamento idêntico)

### 5. i18n

Mover chaves de `session.muteAudio*` para namespace `audio.*` (ex.: `audio.mute`, `audio.unmute`, `audio.muteTitle`, `audio.unmuteTitle`) e atualizar referências — evita label “de sessão” em telas de campanha.

Manter compatibilidade: remover chaves antigas de `session.*` após migração.

---

## Capabilities

### Modified Capabilities

- **audio-user-mute**: controle de mute visível fora da sessão de jogo

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/components/audio/AudioMuteButton.tsx` | Novo |
| `frontend/src/components/layout/AppShell.tsx` | Botão no topnav |
| `frontend/src/app/login/page.tsx` | Botão no layout |
| `frontend/src/app/play/[sessionId]/page.tsx` | Usar componente compartilhado |
| `frontend/messages/pt-BR.json` | Chaves `audio.*` |

---

## Non-Goals

- Slider de volume
- Botão em rotas sem áudio ambiente (ex.: `/register` desativado na fase 1) — pode omitir se layout não justificar
- Alterar lógica de `audioManager` / `AudioRoutingProvider` (já correta)
- Backend

---

## Open Questions

| Questão | Decisão assumida |
|---------|------------------|
| Mostrar mute no login sem autenticação? | Sim — menu pode tocar antes do login |
| Ícone-only no mobile? | Não no MVP — manter texto curto como na sessão |
| Posição no AppShell | Entre email e logout |
