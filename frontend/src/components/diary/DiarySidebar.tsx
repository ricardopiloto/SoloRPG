"use client";

import { useState } from "react";
import type { CampaignNpc, RollHistoryEntry } from "@/lib/api";
import { formatSuccessLevels } from "@/lib/session/rollHistory";
import { t } from "@/lib/i18n";

export function DiarySidebar({
  campaignEntries,
  knownNpcs,
  rollHistory,
}: {
  campaignEntries: Array<{ content: string; created_at?: string }>;
  knownNpcs?: CampaignNpc[];
  rollHistory?: RollHistoryEntry[];
}) {
  const [tab, setTab] = useState<"rolls" | "campaign" | "character">("rolls");

  return (
    <div className="flex flex-col h-full p-4 min-h-0">
      <div className="flex shrink-0 border-b border-wfrp-border" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "rolls"}
          className={`tab-btn ${tab === "rolls" ? "is-active" : ""}`}
          onClick={() => setTab("rolls")}
        >
          Rolagens
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "campaign"}
          className={`tab-btn ${tab === "campaign" ? "is-active" : ""}`}
          onClick={() => setTab("campaign")}
        >
          Campanha
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "character"}
          className={`tab-btn ${tab === "character" ? "is-active" : ""}`}
          onClick={() => setTab("character")}
        >
          Personagem
        </button>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto mt-3 space-y-2 text-sm">
        {tab === "rolls" && (
          <>
            {rollHistory?.length ? (
              rollHistory
                .slice()
                .reverse()
                .map((entry, i) => <RollEntry key={i} entry={entry} />)
            ) : (
              <p className="text-wfrp-muted text-xs">Nenhuma rolagem ainda.</p>
            )}
          </>
        )}

        {tab === "campaign" &&
          (campaignEntries.length ? (
            campaignEntries.map((e, i) => (
              <article key={i} className="border-b border-wfrp-border/50 pb-2">
                <p className="text-wfrp-fg leading-relaxed">{e.content}</p>
              </article>
            ))
          ) : (
            <p className="text-wfrp-muted text-xs">Nenhuma entrada ainda.</p>
          ))}

        {tab === "character" &&
          (knownNpcs?.length ? (
            knownNpcs.map((npc) => <NpcEntry key={npc.id} npc={npc} />)
          ) : (
            <p className="text-wfrp-muted text-xs">{t("diary.noNpcs")}</p>
          ))}
      </div>
    </div>
  );
}

function NpcEntry({ npc }: { npc: CampaignNpc }) {
  const displayName = npc.known_name?.trim() || npc.name;
  const location = npc.met_location?.trim();
  const role = npc.role?.trim();
  const subtitle = [location, role].filter(Boolean).join(" · ");

  return (
    <article className="border-b border-wfrp-border/40 pb-2 last:border-0">
      <p className="font-medium text-wfrp-fg leading-snug">{displayName}</p>
      {subtitle ? <p className="text-xs text-wfrp-muted mt-0.5">{subtitle}</p> : null}
    </article>
  );
}

function RollEntry({ entry }: { entry: RollHistoryEntry }) {
  const successColor = entry.success ? "text-green-400" : "text-red-400";
  const successLabel = entry.success ? "Sucesso" : "Falha";
  const levelLabel = formatSuccessLevels(entry.levels);

  return (
    <article className="border-b border-wfrp-border/40 pb-2 last:border-0">
      <div className="flex items-baseline justify-between gap-1 mb-0.5">
        <span className="font-medium text-wfrp-fg truncate">{entry.label}</span>
        {entry.spontaneous && (
          <span className="text-[9px] uppercase tracking-widest text-wfrp-muted shrink-0">
            Espontânea
          </span>
        )}
      </div>
      <div className="flex items-center gap-2 font-mono text-xs">
        <span className="text-wfrp-highlight text-base font-bold">{entry.roll}</span>
        <span className="text-wfrp-muted">vs {entry.target}</span>
        <span className={`ml-auto ${successColor} font-semibold`}>
          {successLabel} {levelLabel}
        </span>
      </div>
    </article>
  );
}
