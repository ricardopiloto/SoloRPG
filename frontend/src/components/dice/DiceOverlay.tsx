"use client";

import { useEffect, useRef, useState } from "react";
import { ensureDiceBox, preloadDiceBox, safeClear } from "@/lib/dice/diceBoxHost";

type RollResult = { total: number; success?: boolean; sl?: number };

interface Props {
  visible: boolean;
  label?: string;
  meta?: string;
  target?: number;
  onDone: (roll: number) => void;
}

const STAGE_ID = "wfrp-dice-stage";
const STAGE_SELECTOR = `#${STAGE_ID}`;
const HOLD_MS = 1800;

function parseD100(groups: Array<{ value?: number; rolls?: Array<{ value?: number }> }>): number {
  const raw = (groups?.[0]?.value ?? groups?.[0]?.rolls?.[0]?.value ?? 100) as number;
  return raw === 0 ? 100 : Math.max(1, Math.min(100, raw));
}

function buildResult(total: number, target: number | undefined): RollResult {
  const success = target != null ? total <= target : undefined;
  const sl = success ? Math.floor((target! - total) / 10) + 1 : 0;
  return { total, success, sl };
}

export function DiceOverlay({ visible, label, meta, target, onDone }: Props) {
  const [result, setResult] = useState<RollResult | null>(null);
  const [initializing, setInitializing] = useState(false);
  const [diceUnavailable, setDiceUnavailable] = useState(false);
  const onDoneRef = useRef(onDone);
  const targetRef = useRef(target);

  useEffect(() => { onDoneRef.current = onDone; }, [onDone]);
  useEffect(() => { targetRef.current = target; }, [target]);

  // Preload DiceBox as soon as the play page mounts (container is always in DOM).
  useEffect(() => {
    preloadDiceBox(STAGE_SELECTOR);
  }, []);

  const lastVisibleRef = useRef(false);
  useEffect(() => {
    const was = lastVisibleRef.current;
    lastVisibleRef.current = visible;

    if (visible && !was) {
      setResult(null);
      setDiceUnavailable(false);
      setInitializing(true);
      void (async () => {
        try {
          const box = await ensureDiceBox(STAGE_SELECTOR);
          if (!box) {
            setDiceUnavailable(true);
            throw new Error("DiceBox unavailable");
          }
          safeClear(box);
          const groups = await box.roll("1d100");
          const total = parseD100(groups);
          setResult(buildResult(total, targetRef.current));
        } catch (e) {
          console.error("[DiceOverlay] roll failed:", e);
          const total = Math.floor(Math.random() * 100) + 1;
          setResult(buildResult(total, targetRef.current));
        } finally {
          setInitializing(false);
        }
      })();
    }

    if (!visible && was) {
      setResult(null);
      setInitializing(false);
      void ensureDiceBox(STAGE_SELECTOR).then((box) => {
        if (box) safeClear(box);
      });
    }
  }, [visible]);

  useEffect(() => {
    if (!result) return;
    const t = setTimeout(() => onDoneRef.current(result.total), HOLD_MS);
    return () => clearTimeout(t);
  }, [result]);

  return (
    <>
      <div
        id={STAGE_ID}
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none transition-opacity duration-300 dice-overlay-stage"
        style={{ zIndex: visible ? 49 : -1, opacity: visible ? 1 : 0 }}
      />

      {visible && (
        <div
          className="absolute inset-0 pointer-events-none"
          style={{ zIndex: 48, background: "rgba(10, 8, 6, 0.88)" }}
        />
      )}

      {visible && (
        <div
          className="absolute inset-0 flex flex-col pointer-events-none"
          style={{ zIndex: 50 }}
          aria-live="assertive"
          aria-atomic="true"
        >
          <div className="flex flex-col items-center pt-10 gap-1 px-4 text-center">
            {label && (
              <p className="font-display text-xl text-wfrp-fg drop-shadow">{label}</p>
            )}
            {meta && (
              <p className="font-mono text-[11px] text-wfrp-muted tracking-wide">{meta}</p>
            )}
          </div>

          <div className="flex-1" />

          {initializing && !result && !diceUnavailable && (
            <p className="text-center font-mono text-xs text-wfrp-muted animate-pulse pb-10">
              Preparando dados…
            </p>
          )}

          {diceUnavailable && !result && (
            <p className="text-center font-mono text-xs text-wfrp-muted pb-10">
              Dados físicos indisponíveis — usando resultado numérico
            </p>
          )}

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
