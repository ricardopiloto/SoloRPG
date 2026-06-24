# Design: add-global-audio-mute-button

## Layout

```
AppShell topnav (lobby)
  [Logo] [nav links]     [email] [🔇 Silenciar] [Logout] [Nova campanha]

game-header (sessão)
  [título]               [timer] [⏸ Pausar] [🔇 Silenciar]

login (sem AppShell)
  [🔇 Silenciar]                    (canto superior direito, absolute/flex)
  [formulário central]
```

## Componente

```tsx
// AudioMuteButton.tsx
export function AudioMuteButton({ className }: { className?: string }) {
  const { muted, toggleMute } = useAudioMute();
  return (
    <button type="button" onClick={toggleMute} title={...} className={...}>
      {muted ? t("audio.unmute") : t("audio.mute")}
    </button>
  );
}
```

Estilos base extraídos do botão existente em `play/[sessionId]/page.tsx` para uma única fonte de verdade.

## Sincronização de estado

`useAudioMute` já subscreve `audioManager.subscribe()` — múltiplas instâncias do botão (ex.: transição play → campanhas) mostram o mesmo estado sem prop drilling.

## Rotas sem botão

- `/play/...` — mantém botão no `game-header` (não no AppShell; play não usa AppShell)
- Rotas públicas futuras sem música — botão opcional; não prejudica se presente
