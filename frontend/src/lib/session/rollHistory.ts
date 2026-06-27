import type { RollHistoryEntry, SessionTurnOut, TurnResponse } from "@/lib/api";
import { t } from "@/lib/i18n";

type RollResult = TurnResponse["roll_results"][number];

/** PT-BR label for WFRP success/failure level count in roll history. */
export function formatSuccessLevels(count: number): string {
  if (count <= 0) return "";
  return count === 1
    ? t("session.successLevelOne", { count: 1 })
    : t("session.successLevelMany", { count });
}

function rollResultToEntry(
  r: RollResult,
  options: { spontaneous?: boolean; timestamp: number; label?: string }
): RollHistoryEntry | null {
  if (r.roll === undefined || r.target === undefined) return null;
  const levels = typeof r.levels === "number" ? r.levels : 1;
  return {
    label: options.label ?? r.skill ?? r.attribute ?? r.type ?? "Rolagem",
    roll: r.roll,
    target: r.target,
    success: r.success ?? false,
    levels,
    type: r.type,
    spontaneous: options.spontaneous,
    timestamp: options.timestamp,
  };
}

export function rollsToHistoryEntries(
  rolls: TurnResponse["roll_results"],
  options: { spontaneous?: boolean; timestamp?: number } = {}
): RollHistoryEntry[] {
  if (!rolls?.length) return [];
  const timestamp = options.timestamp ?? Date.now();
  return rolls
    .map((r) => rollResultToEntry(r, { spontaneous: options.spontaneous, timestamp }))
    .filter((e): e is RollHistoryEntry => e !== null);
}

export function buildRollHistoryFromTurns(turns: SessionTurnOut[]): RollHistoryEntry[] {
  const entries: RollHistoryEntry[] = [];
  for (const turn of turns) {
    const meta = turn.metadata;
    if (!meta) continue;
    const timestamp = Date.parse(turn.created_at) || Date.now();

    if (turn.role === "gm") {
      const rolls = meta.rolls as TurnResponse["roll_results"] | undefined;
      if (Array.isArray(rolls)) {
        entries.push(...rollsToHistoryEntries(rolls, { timestamp }));
      }
    }

    if (turn.role === "system" && meta.quick_roll) {
      const qr = meta.quick_roll as Record<string, unknown>;
      if (typeof qr.roll === "number" && typeof qr.target === "number") {
        const entry = rollResultToEntry(
          {
            type: (qr.type as string) || "quick_roll",
            roll: qr.roll,
            target: qr.target,
            success: qr.success as boolean | undefined,
            levels: typeof qr.levels === "number" ? qr.levels : undefined,
            skill: typeof qr.key === "string" ? qr.key : undefined,
          },
          {
            spontaneous: true,
            timestamp,
            label: typeof qr.key === "string" ? qr.key : undefined,
          }
        );
        if (entry) entries.push(entry);
      }
    }
  }
  return entries;
}

export function appendRollHistory(
  prev: RollHistoryEntry[],
  rolls: TurnResponse["roll_results"],
  spontaneous = false
): RollHistoryEntry[] {
  const next = rollsToHistoryEntries(rolls, { spontaneous });
  return next.length ? [...prev, ...next] : prev;
}
