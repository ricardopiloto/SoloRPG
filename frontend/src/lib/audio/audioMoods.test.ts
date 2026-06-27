import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MOOD_TO_CATEGORY, resolveMoodAction } from "./audioMoods";

describe("audioMoods", () => {
  it("maps all in-game moods to categories", () => {
    assert.equal(MOOD_TO_CATEGORY["tensão"], "tensao");
    assert.equal(MOOD_TO_CATEGORY["combate"], "combate");
    assert.equal(MOOD_TO_CATEGORY["exploração"], "exploracao");
    assert.equal(MOOD_TO_CATEGORY["investigação"], "investigacao");
    assert.equal(MOOD_TO_CATEGORY["horror"], "horror");
    assert.equal(MOOD_TO_CATEGORY["horror_caos"], "horror_caos");
    assert.equal(MOOD_TO_CATEGORY["social"], "social");
    assert.equal(MOOD_TO_CATEGORY["jornada"], "jornada");
  });

  it("resolveMoodAction returns play for combate in session", () => {
    const action = resolveMoodAction("combate", "/play/session-1", false);
    assert.deepEqual(action, { type: "play", category: "combate" });
  });

  it("resolveMoodAction returns stop for normal", () => {
    assert.deepEqual(resolveMoodAction("normal", "/play/session-1", false), { type: "stop" });
  });

  it("resolveMoodAction noop for unknown mood", () => {
    assert.deepEqual(resolveMoodAction("tenso", "/play/session-1", false), { type: "noop" });
  });

  it("resolveMoodAction noop for in-game mood outside play route", () => {
    assert.deepEqual(resolveMoodAction("combate", "/campaigns", false), { type: "noop" });
  });

  it("resolveMoodAction noop when muted", () => {
    assert.deepEqual(resolveMoodAction("horror", "/play/session-1", true), { type: "noop" });
  });

  it("horror and horror_caos map to distinct categories", () => {
    assert.notEqual(MOOD_TO_CATEGORY["horror"], MOOD_TO_CATEGORY["horror_caos"]);
  });
});
