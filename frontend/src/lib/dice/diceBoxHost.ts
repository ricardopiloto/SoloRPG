/**
 * Singleton DiceBox loader — init once, await before roll.
 * Static ESM bundle from /public (webpackIgnore) so workers resolve correctly.
 */

type DiceBoxInstance = {
  init(): Promise<void>;
  roll(notation: string): Promise<Array<{ value?: number; rolls?: Array<{ value?: number }> }>>;
  /** clear() may return void or Promise<void> depending on DiceBox build/state. */
  clear(): void | Promise<void>;
};

/**
 * Defensively call box.clear() — handles both void and Promise<void> return values.
 * Prevents "clear().catch is not a function" TypeError in production DiceBox builds.
 */
export function safeClear(box: DiceBoxInstance): void {
  const r = box.clear() as unknown;
  if (r != null && typeof (r as Promise<void>).catch === "function") {
    void (r as Promise<void>).catch(() => undefined);
  }
}

type DiceBoxCtor = new (config: Record<string, unknown>) => DiceBoxInstance;

let initPromise: Promise<DiceBoxInstance | null> | null = null;
let activeContainer: string | null = null;

async function waitForContainerSize(selector: string, timeoutMs = 8000): Promise<HTMLElement> {
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const el = document.querySelector<HTMLElement>(selector);
    if (el && el.clientWidth > 0 && el.clientHeight > 0) {
      return el;
    }
    if (Date.now() >= deadline) {
      const fallback = document.querySelector<HTMLElement>(selector);
      if (fallback) return fallback;
      throw new Error(`DiceBox container not found: ${selector}`);
    }
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  }
}

async function loadDiceBoxCtor(): Promise<DiceBoxCtor> {
  const url = "/assets/dice-box/dice-box.es.min.js";
  const mod = await import(/* webpackIgnore: true */ url);
  return (mod as { default: DiceBoxCtor }).default;
}

function wfrpConfig(container: string, canvasId: string) {
  return {
    assetPath: "/assets/dice-box/assets/",
    container,
    id: canvasId,
    theme: "default",
    themeColor: "#C9973A",
    scale: 9,
    gravity: 1.5,
    mass: 1,
    friction: 0.8,
    restitution: 0.2,
    lightIntensity: 1.1,
    enableShadows: true,
    offscreen: false,
    origin: typeof window !== "undefined" ? window.location.origin : "",
  };
}

async function createDiceBox(containerSelector: string): Promise<DiceBoxInstance | null> {
  try {
    await waitForContainerSize(containerSelector);
    const DiceBox = await loadDiceBoxCtor();
    const box = new DiceBox(wfrpConfig(containerSelector, "wfrp-dice-canvas"));
    await box.init();
    return box;
  } catch (e) {
    console.error("[diceBoxHost] init failed:", e);
    return null;
  }
}

/** Returns a ready DiceBox or null if init failed. Retries on subsequent calls after failure. */
export function ensureDiceBox(containerSelector: string): Promise<DiceBoxInstance | null> {
  if (initPromise && activeContainer === containerSelector) {
    return initPromise;
  }
  activeContainer = containerSelector;
  initPromise = createDiceBox(containerSelector).then((box) => {
    if (!box) {
      initPromise = null;
    }
    return box;
  });
  return initPromise;
}

/** Preload during play page mount to reduce first-roll latency. */
export function preloadDiceBox(containerSelector: string): void {
  void ensureDiceBox(containerSelector);
}

export function resetDiceBoxForTests(): void {
  initPromise = null;
  activeContainer = null;
}
