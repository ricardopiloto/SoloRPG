import { useEffect, useRef, useState } from "react";

type DiceType = "d4" | "d6" | "d8" | "d10" | "d12" | "d20" | "d100";

const DICE: DiceType[] = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"];

type RollResult = {
  id: string;
  notation: string;
  values: number[];
  total: number;
  at: Date;
};

export function DiceRoller({
  onRoll,
}: {
  onRoll?: (result: RollResult) => void;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const diceBoxRef = useRef<any>(null);
  const [ready, setReady] = useState(false);
  const [selected, setSelected] = useState<DiceType>("d20");
  const [count, setCount] = useState(1);
  const [rolling, setRolling] = useState(false);
  const [lastResult, setLastResult] = useState<RollResult | null>(null);

  useEffect(() => {
    let disposed = false;
    let box: any;

    (async () => {
      const mod = await import("@3d-dice/dice-box");
      const DiceBox = mod.default;
      box = new DiceBox({
        assetPath: "/assets/",
        container: "#dice-stage",
        id: "dice-canvas",
        theme: "default",
        scale: 17,
        gravity: 1.2,
        mass: 1,
        friction: 0.8,
        restitution: 0.2,
        lightIntensity: 1.1,
        shadowTransparency: 0.6,
        themeColor: "#d4a14a",
      });
      try {
        await box.init();
      } catch (e) {
        console.error("DiceBox init failed", e);
        return;
      }
      if (disposed) return;
      diceBoxRef.current = box;
      box.onRollComplete = (results: any[]) => {
        const values = results.map((r) => r.value);
        const total = values.reduce((a, b) => a + b, 0);
        const result: RollResult = {
          id: crypto.randomUUID(),
          notation: results
            .reduce<Record<string, number>>((acc, r) => {
              acc[r.sides === 100 ? "d100" : `d${r.sides}`] =
                (acc[r.sides === 100 ? "d100" : `d${r.sides}`] || 0) + 1;
              return acc;
            }, {}) &&
            (() => {
              const map: Record<string, number> = {};
              results.forEach((r) => {
                const key = r.sides === 100 ? "d100" : `d${r.sides}`;
                map[key] = (map[key] || 0) + 1;
              });
              return Object.entries(map)
                .map(([k, v]) => `${v}${k}`)
                .join(" + ");
            })(),
          values,
          total,
          at: new Date(),
        };
        setLastResult(result);
        setRolling(false);
        onRoll?.(result);
      };
      setReady(true);
    })();

    return () => {
      disposed = true;
      try {
        box?.clear?.();
      } catch {}
    };
  }, [onRoll]);

  const roll = async (notation?: string) => {
    if (!diceBoxRef.current || rolling) return;
    const n = notation ?? `${count}${selected}`;
    setRolling(true);
    try {
      await diceBoxRef.current.roll(n);
    } catch (e) {
      console.error(e);
      setRolling(false);
    }
  };

  const clear = () => {
    diceBoxRef.current?.clear?.();
    setLastResult(null);
  };

  return (
    <div className="relative flex h-full w-full flex-col">
      {/* Stage */}
      <div className="panel relative flex-1 overflow-hidden">
        <div
          id="dice-stage"
          ref={containerRef}
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse at center, oklch(0.32 0.05 50 / 0.85), oklch(0.14 0.03 35 / 0.95))",
          }}
        />
        {/* corner ornaments */}
        <div className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-[color:var(--color-gold)]/15 rounded-[inherit]" />

        {/* Result overlay */}
        {lastResult && (
          <div className="pointer-events-none absolute left-1/2 top-6 -translate-x-1/2 text-center">
            <div className="panel-heading">{lastResult.notation}</div>
            <div
              className="mt-1 text-6xl font-bold"
              style={{ color: "var(--color-gold)", fontFamily: "var(--font-display)" }}
            >
              {lastResult.total}
            </div>
            <div className="mt-1 text-xs text-[color:var(--color-muted-foreground)]">
              {lastResult.values.join(" · ")}
            </div>
          </div>
        )}

        {!ready && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="panel-heading animate-pulse">Forging the dice…</div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="mt-4 panel p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {DICE.map((d) => (
              <button
                key={d}
                className={`die-btn ${selected === d ? "active" : ""}`}
                onClick={() => setSelected(d)}
                aria-pressed={selected === d}
              >
                {d.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="stat-label">Qty</span>
              <button
                className="die-btn !h-9 !min-w-9 px-2"
                onClick={() => setCount((c) => Math.max(1, c - 1))}
                aria-label="Decrease"
              >
                −
              </button>
              <span
                className="w-8 text-center text-xl"
                style={{ color: "var(--color-gold)", fontFamily: "var(--font-display)" }}
              >
                {count}
              </span>
              <button
                className="die-btn !h-9 !min-w-9 px-2"
                onClick={() => setCount((c) => Math.min(20, c + 1))}
                aria-label="Increase"
              >
                +
              </button>
            </div>

            <button
              className="die-btn active !h-12 !px-6 text-base"
              disabled={!ready || rolling}
              onClick={() => roll()}
            >
              {rolling ? "Rolling…" : `Roll ${count}${selected}`}
            </button>
            <button
              className="die-btn !h-12 !px-4"
              onClick={clear}
              disabled={!ready}
              title="Clear table"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="ornament-divider my-3" />

        <div className="flex flex-wrap gap-2">
          <span className="stat-label self-center mr-1">Quick rolls</span>
          {[
            "1d20",
            "2d20",
            "1d20+1d4",
            "3d6",
            "4d6",
            "2d10",
            "1d100",
          ].map((n) => (
            <button
              key={n}
              className="die-btn !h-9 text-sm"
              disabled={!ready || rolling}
              onClick={() => roll(n)}
            >
              {n}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export type { RollResult };
