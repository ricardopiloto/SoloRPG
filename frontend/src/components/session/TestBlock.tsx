"use client";

import type { PendingTest } from "@/lib/api";
import { t } from "@/lib/i18n";

export function TestBlock({
  pending,
  onRoll,
  disabled,
}: {
  pending: PendingTest;
  onRoll: () => void;
  disabled?: boolean;
}) {
  const p = pending.payload;
  const label = p.pericia || p.descricao || p.atributo || "Teste";
  const mod = p.modificador ?? 0;
  const mandatory = p.obrigatorio === true;

  return (
    <div className="test-block">
      <div className="text-xs uppercase tracking-widest text-wfrp-accent mb-2">
        {mandatory ? "Teste obrigatório" : "Teste solicitado"}
      </div>
      <div className="font-display text-lg mb-1">{label}</div>
      {p.atributo && (
        <div className="text-sm text-wfrp-muted mb-3">
          Atributo: {p.atributo}
          {mod !== 0 && ` · Modificador: ${mod > 0 ? "+" : ""}${mod}`}
        </div>
      )}
      <button
        type="button"
        className="btn-primary w-full"
        onClick={onRoll}
        disabled={disabled}
      >
        {t("session.rollDice")}
      </button>
      {!mandatory && p.opcao_alternativa && (
        <p className="text-wfrp-muted text-sm italic mt-3">
          <span className="not-italic font-medium">Ou:</span>{" "}
          {p.opcao_alternativa}
        </p>
      )}
    </div>
  );
}
