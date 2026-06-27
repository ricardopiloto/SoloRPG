import assert from "node:assert/strict";
import { beforeEach, describe, it } from "node:test";
import { audioManager } from "./audioManager";

const store: Record<string, string> = {};

type MockAudioOptions = {
  playDelayMs?: number;
};

function installBrowserMocks(pathname: string, options: MockAudioOptions = {}) {
  Object.keys(store).forEach((key) => delete store[key]);

  Object.assign(globalThis, {
    localStorage: {
      getItem: (key: string) => store[key] ?? null,
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      removeItem: (key: string) => {
        delete store[key];
      },
    },
    window: {
      location: { pathname },
      addEventListener: () => {},
      removeEventListener: () => {},
    },
    Audio: class MockAudio {
      loop = false;
      volume = 1;
      src = "";
      paused = true;
      static instances: MockAudio[] = [];
      static playDelayMs = options.playDelayMs ?? 0;

      constructor(url?: string) {
        MockAudio.instances.push(this);
        if (url) this.src = url;
      }

      async play() {
        if (MockAudio.playDelayMs > 0) {
          await new Promise<void>((resolve) => setTimeout(resolve, MockAudio.playDelayMs));
        }
        this.paused = false;
      }

      pause() {
        this.paused = true;
      }
    },
  });
}

function audiblyPlayingCount(): number {
  // @ts-expect-error test mock
  return globalThis.Audio.instances.filter((a: { paused: boolean }) => !a.paused).length;
}

describe("audioManager mute", () => {
  beforeEach(() => {
    installBrowserMocks("/campaigns");
    // @ts-expect-error test mock
    globalThis.Audio.instances = [];
    audioManager.resetForTests();
    audioManager.setMuted(false);
  });

  it("persists muted state in localStorage", () => {
    audioManager.setMuted(true);
    assert.equal(audioManager.isMuted(), true);
    assert.equal(store["wfrp-audio-muted"], "true");
  });

  it("play is no-op when muted", async () => {
    audioManager.setMuted(true);
    await audioManager.play("menu");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 0);
  });

  it("menu play is blocked on in-game route when unmuted", async () => {
    installBrowserMocks("/play/session-1");
    audioManager.setMuted(false);
    await audioManager.play("menu");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 0);
  });

  it("unmuting on play route does not auto-start menu", async () => {
    installBrowserMocks("/play/session-1");
    audioManager.setMuted(true);
    audioManager.setMuted(false);
    await audioManager.play("menu");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 0);
  });
});

describe("audioManager menu continuity", () => {
  beforeEach(() => {
    installBrowserMocks("/campaigns");
    // @ts-expect-error test mock
    globalThis.Audio.instances = [];
    audioManager.resetForTests();
    audioManager.setMuted(false);
  });

  it("second play(menu) does not create a new Audio element", async () => {
    await audioManager.play("menu");
    await audioManager.play("menu");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 1);
  });

  it("play(tensao) replaces menu playback when entering session", async () => {
    await audioManager.play("menu");
    assert.equal(audiblyPlayingCount(), 1);
    // @ts-expect-error test mock
    globalThis.window.location.pathname = "/play/session-1";
    await audioManager.play("tensao");
    assert.equal(audiblyPlayingCount(), 1);
    assert.equal(audioManager.getCurrentCategory(), "tensao");
  });

  it("stop then play(menu) creates a new Audio element", async () => {
    await audioManager.play("menu");
    audioManager.stop();
    await audioManager.play("menu");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 2);
  });
});

describe("audioManager mute routing regression", () => {
  beforeEach(() => {
    installBrowserMocks("/campaigns", { playDelayMs: 20 });
    // @ts-expect-error test mock
    globalThis.Audio.instances = [];
    audioManager.resetForTests();
    audioManager.setMuted(false);
  });

  it("setMuted(true) during in-flight play leaves no audible track", async () => {
    const playing = audioManager.play("menu");
    await new Promise<void>((resolve) => setTimeout(resolve, 5));
    audioManager.setMuted(true);
    await playing;
    assert.equal(audiblyPlayingCount(), 0);
    assert.equal(audioManager.isAudiblyPlaying(), false);
  });

  it("concurrent play(menu) calls leave at most one audible track", async () => {
    const first = audioManager.play("menu");
    const second = audioManager.play("menu");
    await Promise.all([first, second]);
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 2);
    assert.equal(audiblyPlayingCount(), 1);
  });

  it("setMuted(true) then play(menu) is a no-op", async () => {
    audioManager.setMuted(true);
    await audioManager.play("menu");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 0);
  });
});

describe("audioManager in-game moods", () => {
  beforeEach(() => {
    installBrowserMocks("/play/session-1");
    // @ts-expect-error test mock
    globalThis.Audio.instances = [];
    audioManager.resetForTests();
    audioManager.setMuted(false);
  });

  function lastAudioSrc(): string {
    // @ts-expect-error test mock
    const instances = globalThis.Audio.instances as { src: string }[];
    return decodeURIComponent(instances[instances.length - 1]?.src ?? "");
  }

  it("play(horror) picks from supernatural pool only", async () => {
    await audioManager.play("horror");
    assert.match(lastAudioSrc(), /SoloRPG - Horror/);
    assert.doesNotMatch(lastAudioSrc(), /Horror Chaos/);
  });

  it("play(horror_caos) picks from chaos pool only", async () => {
    await audioManager.play("horror_caos");
    assert.match(lastAudioSrc(), /Horror Chaos/);
    assert.doesNotMatch(lastAudioSrc(), /SoloRPG - Horror\.mp3$/);
  });

  it("horror idempotent second play does not cross into chaos pool", async () => {
    await audioManager.play("horror");
    await audioManager.play("horror");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 1);
    assert.doesNotMatch(lastAudioSrc(), /Horror Chaos/);
  });

  it("combate then exploracao leaves one audible track", async () => {
    await audioManager.play("combate");
    await audioManager.play("exploracao");
    assert.equal(audiblyPlayingCount(), 1);
    assert.equal(audioManager.getCurrentCategory(), "exploracao");
  });

  it("in-game category blocked outside play route", async () => {
    installBrowserMocks("/campaigns");
    await audioManager.play("combate");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 0);
  });

  it("second play(social) is idempotent", async () => {
    await audioManager.play("social");
    await audioManager.play("social");
    // @ts-expect-error test mock
    assert.equal(globalThis.Audio.instances.length, 1);
  });
});
