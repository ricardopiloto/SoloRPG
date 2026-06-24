"use client";

import { useCallback, useEffect, useState } from "react";
import { audioManager } from "@/lib/audio/audioManager";

export function useAudioMute() {
  const [muted, setMuted] = useState(() =>
    typeof window !== "undefined" ? audioManager.isMuted() : false
  );

  useEffect(() => {
    setMuted(audioManager.isMuted());
    return audioManager.subscribe(() => setMuted(audioManager.isMuted()));
  }, []);

  const toggleMute = useCallback(() => {
    audioManager.setMuted(!audioManager.isMuted());
  }, []);

  return { muted, toggleMute };
}
