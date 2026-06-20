import { t } from "@/lib/i18n";

export function WoundsBar({ current, max }: { current: number; max: number }) {
  const pct = max > 0 ? Math.max(0, (current / max) * 100) : 0;
  return (
    <div className="py-1">
      <div className="flex justify-between text-xs text-wfrp-muted mb-1">
        <span>{t("character.wounds")}</span>
        <span>
          {current}/{max}
        </span>
      </div>
      <div className="wounds-bar">
        <div className="wounds-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
