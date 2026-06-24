import { isInGameRoute } from "./audioRoutes";

export type AudioCategory = "menu" | "tensao";

const TRACKS: Record<AudioCategory, string[]> = {
  menu: ["/audio/Solo RPG Theme.mp3", "/audio/Solo RPG Theme 2.mp3"],
  tensao: ["/audio/Solo RPG - Tension.mp3", "/audio/Solo RPG - Tension 2.mp3"],
};

/** Ambient levels — background only, not foreground music. */
const VOLUME: Record<AudioCategory, number> = {
  menu: 0.12,
  tensao: 0.08,
};

const MUTE_STORAGE_KEY = "wfrp-audio-muted";

let currentAudio: HTMLAudioElement | null = null;
let currentCategory: AudioCategory | null = null;
let pendingCategory: AudioCategory | null = null;
let playGeneration = 0;
let interactionBound = false;
let retryHandler: (() => void) | null = null;
let muted = false;
let mutedLoaded = false;
const muteListeners = new Set<() => void>();

function ensureMutedLoaded(): void {
  if (mutedLoaded || typeof window === "undefined") return;
  muted = localStorage.getItem(MUTE_STORAGE_KEY) === "true";
  mutedLoaded = true;
}

function notifyMuteListeners(): void {
  muteListeners.forEach((listener) => listener());
}

function encodeTrackPath(path: string): string {
  return "/" + path.split("/").filter(Boolean).map(encodeURIComponent).join("/");
}

function isPlaying(): boolean {
  return currentAudio != null && !currentAudio.paused;
}

function disposeAudio(audio: HTMLAudioElement): void {
  audio.pause();
  audio.src = "";
}

function cancelInteractionRetry(): void {
  if (typeof window === "undefined") return;
  if (retryHandler) {
    window.removeEventListener("click", retryHandler);
    window.removeEventListener("keydown", retryHandler);
    retryHandler = null;
  }
  interactionBound = false;
  pendingCategory = null;
}

function bindInteractionRetry(): void {
  if (interactionBound || typeof window === "undefined") return;
  interactionBound = true;

  const retry = () => {
    cancelInteractionRetry();
    if (pendingCategory && !muted) {
      const category = pendingCategory;
      pendingCategory = null;
      void audioManager.play(category);
    }
  };

  retryHandler = retry;
  window.addEventListener("click", retry, { once: true });
  window.addEventListener("keydown", retry, { once: true });
}

function invalidatePlayback(): void {
  playGeneration++;
  cancelInteractionRetry();
  if (currentAudio) {
    disposeAudio(currentAudio);
    currentAudio = null;
  }
  currentCategory = null;
}

export const audioManager = {
  isMuted(): boolean {
    ensureMutedLoaded();
    return muted;
  },

  isAudiblyPlaying(): boolean {
    return isPlaying();
  },

  setMuted(value: boolean): void {
    ensureMutedLoaded();
    muted = value;
    if (typeof window !== "undefined") {
      localStorage.setItem(MUTE_STORAGE_KEY, value ? "true" : "false");
    }
    if (value) {
      invalidatePlayback();
    }
    notifyMuteListeners();
  },

  subscribe(listener: () => void): () => void {
    muteListeners.add(listener);
    return () => muteListeners.delete(listener);
  },

  async play(category: AudioCategory): Promise<void> {
    if (typeof window === "undefined") return;
    ensureMutedLoaded();
    if (muted) return;
    if (category === "menu" && isInGameRoute(window.location.pathname)) return;

    if (currentCategory === category && isPlaying()) {
      return;
    }

    invalidatePlayback();
    const gen = playGeneration;

    const tracks = TRACKS[category];
    const src = tracks[Math.floor(Math.random() * tracks.length)];
    const audio = new Audio(encodeTrackPath(src));
    audio.loop = true;
    audio.volume = VOLUME[category];

    try {
      await audio.play();
      if (gen !== playGeneration || muted) {
        disposeAudio(audio);
        return;
      }
      if (category === "menu" && isInGameRoute(window.location.pathname)) {
        disposeAudio(audio);
        return;
      }
      currentAudio = audio;
      currentCategory = category;
      pendingCategory = null;
    } catch (error) {
      disposeAudio(audio);
      if (gen !== playGeneration || muted) return;
      if (error instanceof DOMException && error.name === "NotAllowedError") {
        pendingCategory = category;
        bindInteractionRetry();
      }
    }
  },

  stop(): void {
    invalidatePlayback();
  },

  /** Test-only reset of playback state. */
  resetForTests(): void {
    playGeneration = 0;
    invalidatePlayback();
  },
};
