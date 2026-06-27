import type { AudioCategory } from "./audioManager";
import { isInGameRoute } from "./audioRoutes";

/** GM `mood` / `scene_mood` → internal `AudioCategory` (ASCII slug). */
export const MOOD_TO_CATEGORY: Record<string, AudioCategory> = {
  "tensão": "tensao",
  combate: "combate",
  "exploração": "exploracao",
  "investigação": "investigacao",
  horror: "horror",
  horror_caos: "horror_caos",
  social: "social",
  jornada: "jornada",
};

export type MoodAction =
  | { type: "play"; category: AudioCategory }
  | { type: "stop" }
  | { type: "noop" };

export function moodToCategory(mood: string): AudioCategory | null {
  return MOOD_TO_CATEGORY[mood] ?? null;
}

export function resolveMoodAction(
  mood: string,
  pathname: string,
  isMuted: boolean,
  isInGame: (path: string) => boolean = isInGameRoute
): MoodAction {
  if (isMuted) return { type: "noop" };
  if (mood === "normal") return { type: "stop" };
  const category = moodToCategory(mood);
  if (!category) return { type: "noop" };
  if (!isInGame(pathname)) return { type: "noop" };
  return { type: "play", category };
}
