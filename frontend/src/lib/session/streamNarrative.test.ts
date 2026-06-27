import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { appendNarrativeFromDone } from "./streamNarrative";

describe("appendNarrativeFromDone", () => {
  it("appends final narrative and drops streaming placeholder", () => {
    const prev = [
      { kind: "player" as const, content: "Olá" },
      { kind: "narrative" as const, content: "[MUSICA] partial", streaming: true },
    ];
    const next = appendNarrativeFromDone(prev, {
      narrative: "Severin inclina a cabeça.",
    } as never);
    assert.equal(next.length, 2);
    assert.equal(next[1].kind, "narrative");
    if (next[1].kind === "narrative") {
      assert.equal(next[1].content, "Severin inclina a cabeça.");
      assert.equal(next[1].streaming, undefined);
    }
  });

  it("returns prev without narrative when done has empty narrative", () => {
    const prev = [{ kind: "player" as const, content: "x" }];
    const next = appendNarrativeFromDone(prev, { narrative: "" } as never);
    assert.deepEqual(next, prev);
  });
});
