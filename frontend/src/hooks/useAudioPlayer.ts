"use client";

import { useCallback } from "react";
import { usePathname } from "next/navigation";
import { audioManager } from "@/lib/audio/audioManager";
import { isInGameRoute } from "@/lib/audio/audioRoutes";

export function useAudioPlayer() {
  const pathname = usePathname();

  const setMood = useCallback(
    (mood: string) => {
      if (audioManager.isMuted()) return;
      if (mood === "tensão") {
        if (!isInGameRoute(pathname ?? "")) return;
        void audioManager.play("tensao");
      } else if (mood === "normal") {
        audioManager.stop();
      }
    },
    [pathname]
  );

  const playMenu = useCallback(() => {
    void audioManager.play("menu");
  }, []);

  const stop = useCallback(() => {
    audioManager.stop();
  }, []);

  return { setMood, playMenu, stop };
}
