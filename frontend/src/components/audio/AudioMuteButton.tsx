"use client";

import { useAudioMute } from "@/hooks/useAudioMute";
import { t } from "@/lib/i18n";

const baseClassName =
  "text-xs px-2 py-1 rounded border border-wfrp-border text-wfrp-muted hover:text-wfrp-fg hover:border-wfrp-accent/60 transition-colors";

type AudioMuteButtonProps = {
  className?: string;
};

export function AudioMuteButton({ className }: AudioMuteButtonProps) {
  const { muted, toggleMute } = useAudioMute();

  return (
    <button
      type="button"
      className={className ? `${baseClassName} ${className}` : baseClassName}
      onClick={toggleMute}
      title={muted ? t("audio.unmuteTitle") : t("audio.muteTitle")}
    >
      {muted ? t("audio.unmute") : t("audio.mute")}
    </button>
  );
}
