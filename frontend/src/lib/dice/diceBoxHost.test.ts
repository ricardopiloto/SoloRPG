import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { safeClear } from "./diceBoxHost";

describe("safeClear", () => {
  it("chains .catch when clear() returns a Promise", () => {
    let caught = false;
    const box = {
      clear: () =>
        Promise.reject(new Error("cleanup")).catch(() => {
          caught = true;
        }),
    };
    assert.doesNotThrow(() => safeClear(box as Parameters<typeof safeClear>[0]));
    assert.equal(caught, false);
  });

  it("does not throw when clear() returns void", () => {
    const box = { clear: () => undefined };
    assert.doesNotThrow(() => safeClear(box as Parameters<typeof safeClear>[0]));
  });

  it("swallows rejected Promise from clear()", async () => {
    const box = {
      clear: () => Promise.reject(new Error("cleanup")),
    };
    assert.doesNotThrow(() => safeClear(box as Parameters<typeof safeClear>[0]));
    await new Promise((r) => setTimeout(r, 0));
  });
});
