"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { AuthProvider } from "@/contexts/AuthContext";
import { useAudioMute } from "@/hooks/useAudioMute";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";
import { audioManager } from "@/lib/audio/audioManager";
import { isInGameRoute, isMenuAudioRoute } from "@/lib/audio/audioRoutes";

function AudioRoutingProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { muted } = useAudioMute();
  const { playMenu, stop } = useAudioPlayer();
  const prevPathRef = useRef<string | null>(null);

  useEffect(() => {
    const path = pathname ?? "";
    const prev = prevPathRef.current;
    const pathChanged = prev !== path;
    prevPathRef.current = path;

    const isMuted = audioManager.isMuted();

    if (isMuted || isInGameRoute(path)) {
      stop();
      return;
    }

    if (!isMenuAudioRoute(path)) {
      stop();
      return;
    }

    if (
      pathChanged &&
      prev != null &&
      isMenuAudioRoute(prev) &&
      !isInGameRoute(prev) &&
      audioManager.isAudiblyPlaying()
    ) {
      return;
    }

    playMenu();
  }, [pathname, muted, playMenu, stop]);

  return children;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AudioRoutingProvider>{children}</AudioRoutingProvider>
    </AuthProvider>
  );
}
