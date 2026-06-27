import type { TurnResponse } from "@/lib/api";
import type { ChatEntry } from "@/components/session/ChatLog";

/** Append sanitized GM narrative after SSE done (no streaming partials). */
export function appendNarrativeFromDone(
  prev: ChatEntry[],
  finalResult: TurnResponse | null
): ChatEntry[] {
  if (!finalResult?.narrative) {
    return prev.filter((e) => !(e.kind === "narrative" && e.streaming));
  }
  const trimmed = prev.filter((e) => !(e.kind === "narrative" && e.streaming));
  return [...trimmed, { kind: "narrative", content: finalResult.narrative }];
}
