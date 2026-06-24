# Tasks: add-global-audio-mute-button

## Fase 1 — Componente

- [x] **T1** Criar `frontend/src/components/audio/AudioMuteButton.tsx` extraindo markup/estilo do botão em `play/[sessionId]/page.tsx`
- [x] **T2** Em `messages/pt-BR.json`: adicionar `audio.mute`, `audio.unmute`, `audio.muteTitle`, `audio.unmuteTitle`; remover `session.muteAudio*`

## Fase 2 — Integração UI

- [x] **T3** `AppShell.tsx`: renderizar `<AudioMuteButton />` no topnav quando `user` autenticado
- [x] **T4** `login/page.tsx`: renderizar `<AudioMuteButton />` no layout (canto superior direito)
- [x] **T5** `play/[sessionId]/page.tsx`: substituir botão inline por `<AudioMuteButton />`

## Fase 3 — Validação

- [x] **T6** TypeScript / lint sem erros
- [ ] **T7** Validar manualmente:
  - `/campaigns` com theme tocando → Silenciar para o áudio; refresh mantém muted
  - Reativar som em `/campaigns` → theme retoma
  - `/login` → botão visível e funcional
  - `/play/...` → botão continua ao lado de Pausar; comportamento inalterado
  - Navegar play → campanhas → ambos os contextos refletem mesmo estado muted
