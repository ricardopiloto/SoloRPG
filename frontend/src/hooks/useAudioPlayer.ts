"use client";

import { useCallback } from "react";
import { usePathname } from "next/navigation";
import { audioManager } from "@/lib/audio/audioManager";
import { resolveMoodAction } from "@/lib/audio/audioMoods";

export function useAudioPlayer() {
  const pathname = usePathname();

  const setMood = useCallback(
    (mood: string) => {
      const action = resolveMoodAction(mood, pathname ?? "", audioManager.isMuted());
      if (action.type === "play") {
        void audioManager.play(action.category);
      } else if (action.type === "stop") {
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
