"use client";

import { useEffect, useRef, useState } from "react";

type RollResult = { total: number; success?: boolean; sl?: number };

interface Props {
  visible: boolean;
  label?: string;
  meta?: string;
  target?: number;
  onDone: (roll: number) => void;
}

const STAGE_ID = "wfrp-dice-stage";
const HOLD_MS = 1800;

export function DiceOverlay({ visible, label, meta, target, onDone }: Props) {
  const diceBoxRef = useRef<any>(null);
  const [result, setResult] = useState<RollResult | null>(null);
  const [initializing, setInitializing] = useState(false);
  const onDoneRef = useRef(onDone);
  const targetRef = useRef(target);

  useEffect(() => { onDoneRef.current = onDone; }, [onDone]);
  useEffect(() => { targetRef.current = target; }, [target]);

  // Initialize DiceBox once on mount.
  // The #STAGE_ID container is always in the DOM so DiceBox can attach its canvas.
  useEffect(() => {
    setInitializing(true);
    void (async () => {
      try {
        // Load from pre-built ESM bundle so web worker scripts resolve correctly
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const url = "/assets/dice-box/dice-box.es.min.js";
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const mod = await import(/* webpackIgnore: true */ url as any);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
        const DiceBox = (mod as any).default;
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call
        const box = new DiceBox({
          assetPath: "/assets/dice-box/assets/",
          container: `#${STAGE_ID}`,
          id: "wfrp-dice-canvas",
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
        });
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
        await box.init();
        diceBoxRef.current = box;
      } catch (e) {
        console.error("[DiceOverlay] init failed:", e);
      } finally {
        setInitializing(false);
      }
    })();
  }, []);

  // Trigger a roll each time visible transitions false → true
  const lastVisibleRef = useRef(false);
  useEffect(() => {
    const was = lastVisibleRef.current;
    lastVisibleRef.current = visible;

    if (visible && !was) {
      setResult(null);
      void (async () => {
        try {
          const box = diceBoxRef.current;
          if (!box) throw new Error("not ready");
          // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
          box.clear();
          // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-explicit-any
          const groups: any[] = await box.roll("1d100");
          // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
          const raw = (groups?.[0]?.value ?? 100) as number;
          const total = raw === 0 ? 100 : Math.max(1, Math.min(100, raw));
          const t = targetRef.current;
          const success = t != null ? total <= t : undefined;
          const sl = success ? Math.floor((t! - total) / 10) + 1 : 0;
          setResult({ total, success, sl });
        } catch (e) {
          console.error("[DiceOverlay] roll failed:", e);
          // Software fallback so the game never freezes
          const total = Math.floor(Math.random() * 100) + 1;
          const t = targetRef.current;
          const success = t != null ? total <= t : undefined;
          const sl = success ? Math.floor((t! - total) / 10) + 1 : 0;
          setResult({ total, success, sl });
        }
      })();
    }

    if (!visible && was) {
      setResult(null);
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      try { diceBoxRef.current?.clear?.(); } catch { /* ignore */ }
    }
  }, [visible]);

  // Hold result on screen then report to caller
  useEffect(() => {
    if (!result) return;
    const t = setTimeout(() => onDoneRef.current(result.total), HOLD_MS);
    return () => clearTimeout(t);
  }, [result]);

  return (
    <>
      {/*
       * Canvas host — always mounted so DiceBox.init() can attach its canvas.
       * z-index changes: -1 (hidden behind chat) vs 49 (above dark background).
       * opacity fades in/out for a smooth transition.
       */}
      <div
        id={STAGE_ID}
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none transition-opacity duration-300"
        style={{ zIndex: visible ? 49 : -1, opacity: visible ? 1 : 0 }}
      />

      {/* Dark backdrop — between chat content and canvas */}
      {visible && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ zIndex: 48, background: "rgba(10, 8, 6, 0.88)" }}
        />
      )}

      {/* Info UI — label, meta, result — above the canvas */}
      {visible && (
        <div
          className="absolute inset-0 flex flex-col pointer-events-none"
          style={{ zIndex: 50 }}
          aria-live="assertive"
          aria-atomic="true"
        >
          {/* Roll context at the top */}
          <div className="flex flex-col items-center pt-10 gap-1 px-4 text-center">
            {label && (
              <p className="font-display text-xl text-wfrp-fg drop-shadow">{label}</p>
            )}
            {meta && (
              <p className="font-mono text-[11px] text-wfrp-muted tracking-wide">{meta}</p>
            )}
          </div>

          <div className="flex-1" />

          {/* Initializing state */}
          {initializing && (
            <p className="text-center font-mono text-xs text-wfrp-muted animate-pulse pb-10">
              Preparando dados…
            </p>
          )}

          {/* Result shown after physics settle */}
          {result && (
            <div className="flex flex-col items-center pb-10 gap-1">
              <p className="font-mono text-sm text-wfrp-muted">
                Rolagem:{" "}
                <strong className="text-wfrp-fg text-lg">{result.total}</strong>
                {target != null && (
                  <>
                    {" "}
                    · Alvo: <strong>{target}</strong>
                  </>
                )}
              </p>
              {result.success != null && (
                <p
                  className={`font-mono text-[13px] uppercase tracking-widest ${
                    result.success ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {result.success ? `Sucesso · SL ${result.sl ?? 0}` : "Falha"}
                </p>
              )}
            </div>
          )}

          <span className="sr-only">
            {result ? `Resultado da rolagem: ${result.total}` : "Rolando dados..."}
          </span>
        </div>
      )}
    </>
  );
}
