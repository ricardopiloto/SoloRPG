"use client";

import { t } from "@/lib/i18n";

export function SessionPrepareOverlay({
  minutes,
  onStart,
}: {
  minutes: number;
  onStart: () => void;
}) {
  return (
    <div className="fixed inset-0 z-[100] grid place-items-center bg-black/80 p-4">
      <div className="card-wfrp max-w-md w-full text-center p-8">
        <h2 className="font-display text-2xl mb-4">{t("session.prepareTitle")}</h2>
        <p className="text-wfrp-muted mb-6 leading-relaxed">
          {t("session.prepareBody", { minutes })}
        </p>
        <button type="button" className="btn-primary w-full" onClick={onStart}>
          {t("session.prepareStart")}
        </button>
      </div>
    </div>
  );
}
