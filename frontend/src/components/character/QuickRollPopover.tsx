"use client";

import { useState } from "react";
import { t } from "@/lib/i18n";

export type QuickRollTarget = {
  type: "attribute" | "skill" | "weapon";
  key: string;
  label: string;
  target: number;
};

export function QuickRollPopover({
  target,
  onRoll,
  onCancel,
}: {
  target: QuickRollTarget;
  onRoll: (modifier: number) => void | Promise<void>;
  onCancel: () => void;
}) {
  const [modifier, setModifier] = useState(0);
  const [rolling, setRolling] = useState(false);

  const effectiveTarget = Math.max(1, Math.min(100, target.target + modifier));

  return (
    <div className="quick-roll-popover" role="dialog" aria-label={t("session.quickRoll")}>
      <div className="font-display text-xs uppercase tracking-wider text-wfrp-accent mb-2">
        {target.label}
      </div>
      <div className="font-mono text-sm mb-3">
        {t("session.target")}: <strong>{effectiveTarget}</strong>
      </div>
      <label className="block text-xs text-wfrp-muted mb-3">
        {t("session.modifier")}
        <div className="flex items-center gap-2 mt-1">
          <button
            type="button"
            className="w-8 h-8 border border-wfrp-border rounded"
            onClick={() => setModifier((m) => Math.max(-30, m - 5))}
          >
            −
          </button>
          <input
            type="number"
            className="w-16 text-center bg-wfrp-bg border border-wfrp-border rounded py-1"
            value={modifier}
            min={-30}
            max={30}
            onChange={(e) => setModifier(Number(e.target.value))}
          />
          <button
            type="button"
            className="w-8 h-8 border border-wfrp-border rounded"
            onClick={() => setModifier((m) => Math.min(30, m + 5))}
          >
            +
          </button>
        </div>
      </label>
      <div className="flex gap-2">
        <button
          type="button"
          className="btn-primary flex-1 text-sm"
          onClick={() => {
            setRolling(true);
            void onRoll(modifier);
          }}
        >
          {t("session.rollNow")}
        </button>
        <button type="button" className="btn-secondary text-sm" onClick={onCancel}>
          {t("session.cancel")}
        </button>
      </div>
    </div>
  );
}
