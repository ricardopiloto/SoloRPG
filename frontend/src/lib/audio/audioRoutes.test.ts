import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { isInGameRoute, isMenuAudioRoute, normalizePath } from "./audioRoutes";

describe("normalizePath", () => {
  it("keeps root as /", () => {
    assert.equal(normalizePath("/"), "/");
    assert.equal(normalizePath(""), "/");
  });

  it("strips trailing slash", () => {
    assert.equal(normalizePath("/campaigns/"), "/campaigns");
  });
});

describe("isInGameRoute", () => {
  it("matches play session paths", () => {
    assert.equal(isInGameRoute("/play/abc-123"), true);
  });

  it("rejects lobby paths", () => {
    assert.equal(isInGameRoute("/campaigns"), false);
  });
});

describe("isMenuAudioRoute", () => {
  it("allows known lobby routes", () => {
    assert.equal(isMenuAudioRoute("/"), true);
    assert.equal(isMenuAudioRoute("/campaigns"), true);
    assert.equal(isMenuAudioRoute("/character"), true);
    assert.equal(isMenuAudioRoute("/session/end"), true);
  });

  it("rejects play and unknown routes", () => {
    assert.equal(isMenuAudioRoute("/play/uuid"), false);
    assert.equal(isMenuAudioRoute("/settings"), false);
  });
});
