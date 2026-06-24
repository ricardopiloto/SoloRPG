# Design: add-ambient-audio-engine

## Fluxo de dados

```
LLM response
  └── [MUSICA]{"mood":"tensão"}
        └── gm_orchestrator._handle_signal("MUSICA")
              └── TurnResult.scene_mood = "tensão"
                    └── SSE done payload: { scene_mood: "tensão", ... }
                          └── useSessionPlay → setMood("tensão")
                                └── AudioManager.play("tensão")
                                      └── <audio> element → Tension track em loop
```

## AudioManager (singleton)

```
audioManager.ts
  ├── tracks: { menu: [...], tensão: [...] }
  ├── volume: menu 0.3, tensão 0.22 (ambiente — não foreground)
  ├── currentAudio: HTMLAudioElement | null
  ├── play(category) → stop atual → pick random → loop
  └── stop() → pause + nullify
```

Singleton module-level (não React) — sobrevive a re-renders e mudanças de rota sem perder o estado de playback. Criado lazily no primeiro uso (garante que `window`/`Audio` existam — Next.js SSR safe).

## Routing Logic

> **Atualizado por `restrict-menu-audio-out-of-play`:** menu theme usa allowlist explícita (`audioRoutes.ts`); mute global via `wfrp-audio-muted` em `localStorage`; botão Silenciar no header da sessão.

```
providers.tsx (AudioRoutingProvider)
  └── usePathname()
        ├── path starts with /play/ → stop()
        └── else → play("menu")

useSessionPlay.ts
  └── on turn response with scene_mood
        ├── "tensão" → play("tensão")
        └── "normal" → stop()

AuthContext logout handler
  └── stop()
```

## Signal `[MUSICA]` no backend

O sinal é processado em `_handle_signal` como qualquer outro. O `mood` é colocado em `TurnResult.scene_mood`. Sinais inválidos (mood desconhecido) são ignorados silenciosamente.

O sinal é emitido pelo LLM — **não** há análise pós-processamento do texto. A instrução no system prompt define os critérios para que o GM decida emitir.

## Assets

```
Projeto root
  audio/
    Solo RPG Theme.mp3
    Solo RPG Theme 2.mp3
    Solo RPG - Tension.mp3
    Solo RPG - Tension 2.mp3

Docker build (context: .)
  frontend/Dockerfile
    COPY audio ./public/audio/   ← acessível em /audio/*.mp3 no browser

Local dev
  npm run prepare:audio   ← copia ../audio/*.mp3 → public/audio/
  (ou fazer parte de postinstall)
```

## Limitação: Autoplay Policy

Browsers modernos (Chrome, Firefox, Safari) bloqueiam `audio.play()` antes de qualquer interação do usuário. A interação com qualquer botão na tela de login ou campanhas é suficiente para desbloquear o autoplay para aquela sessão de browser. Não há solução perfeita sem um clique explícito "ativar som".

Mitigação: na primeira tentativa de `play()` que falhar com `NotAllowedError`, silenciosamente enfileirar a track e tentar novamente no próximo evento de interação (`click`, `keydown`) via listener único.
