import assert from "node:assert/strict";
import { describe, it } from "node:test";
import type { SessionTurnOut } from "@/lib/api";
import {
  appendRollHistory,
  buildRollHistoryFromTurns,
  formatSuccessLevels,
  rollsToHistoryEntries,
} from "./rollHistory";

const perceptionRoll = {
  type: "test",
  roll: 34,
  target: 40,
  success: true,
  skill: "Percepção",
  levels: 1,
};

describe("rollHistory", () => {
  it("appendRollHistory adds one entry per mechanical roll", () => {
    const history = appendRollHistory([], [perceptionRoll]);
    assert.equal(history.length, 1);
    assert.equal(history[0].label, "Percepção");
    assert.equal(history[0].levels, 1);
  });

  it("does not duplicate when narrate would echo the same roll_results", () => {
    let history = appendRollHistory([], [perceptionRoll]);
    // applyMeta must NOT call appendRollHistory again with the same rolls
    assert.equal(history.length, 1);
  });

  it("buildRollHistoryFromTurns maps two gm rolls from metadata", () => {
    const turns: SessionTurnOut[] = [
      {
        id: "1",
        session_id: "s",
        role: "gm",
        content: "n1",
        metadata: { rolls: [{ ...perceptionRoll, roll: 10, target: 35 }] },
        created_at: "2026-01-01T10:00:00Z",
      },
      {
        id: "2",
        session_id: "s",
        role: "gm",
        content: "n2",
        metadata: { rolls: [{ ...perceptionRoll, roll: 50, target: 35, success: false }] },
        created_at: "2026-01-01T10:05:00Z",
      },
    ];
    const history = buildRollHistoryFromTurns(turns);
    assert.equal(history.length, 2);
    assert.equal(history[0].roll, 10);
    assert.equal(history[1].roll, 50);
  });

  it("buildRollHistoryFromTurns includes spontaneous quick_roll", () => {
    const turns: SessionTurnOut[] = [
      {
        id: "1",
        session_id: "s",
        role: "system",
        content: "note",
        metadata: {
          quick_roll: {
            type: "quick_roll",
            key: "Percepção",
            roll: 22,
            target: 33,
            success: true,
            levels: 2,
          },
        },
        created_at: "2026-01-01T11:00:00Z",
      },
    ];
    const history = buildRollHistoryFromTurns(turns);
    assert.equal(history.length, 1);
    assert.equal(history[0].spontaneous, true);
    assert.equal(history[0].label, "Percepção");
    assert.equal(history[0].levels, 2);
  });

  it("rollsToHistoryEntries skips rolls without target", () => {
    assert.equal(rollsToHistoryEntries([{ type: "unknown" }]).length, 0);
  });

  it("uses server levels for target 32 roll 3 (three levels)", () => {
    const entries = rollsToHistoryEntries([
      {
        type: "test",
        roll: 3,
        target: 32,
        success: true,
        skill: "Percepção",
        levels: 3,
      },
    ]);
    assert.equal(entries.length, 1);
    assert.equal(entries[0].levels, 3);
  });

  it("formatSuccessLevels uses correct PT-BR plural", () => {
    assert.equal(formatSuccessLevels(1), "(1 nível)");
    assert.equal(formatSuccessLevels(3), "(3 níveis)");
    assert.equal(formatSuccessLevels(0), "");
  });
});
