"use client";

import { useEffect, useState } from "react";
import { api, type Character } from "@/lib/api";
import { t } from "@/lib/i18n";
import { computeSkillTarget, type SkillCatalogEntry } from "@/lib/wfrp-attributes";
import { AttributeCards } from "./AttributeCards";
import { CollapsibleSection } from "./CollapsibleSection";
import { FateGems } from "./FateGems";
import { WoundsBar } from "./WoundsBar";
import { TruncatedText } from "@/components/ui/TruncatedText";
import { QuickRollPopover, type QuickRollTarget } from "./QuickRollPopover";

export function CharacterSidebar({
  character,
  sessionMode,
  combatState,
  timeRemaining,
  quickRollDisabled,
  onQuickRoll,
}: {
  character: Character;
  sessionMode?: string;
  combatState?: { turn: number; order: Array<{ nome: string; initiative: number }>; current_index: number } | null;
  timeRemaining?: number;
  quickRollDisabled?: boolean;
  onQuickRoll: (target: QuickRollTarget, modifier: number) => Promise<void>;
}) {
  const career = character.careers[0];
  const [popover, setPopover] = useState<QuickRollTarget | null>(null);
  const [skillCatalog, setSkillCatalog] = useState<SkillCatalogEntry[]>([]);

  useEffect(() => {
    api.listSkills().then((res) => setSkillCatalog(res.skills));
  }, []);

  const ownedAdvances = Object.fromEntries(
    character.skills.map((s) => [s.name, s.advances])
  );

  return (
    <div className="text-sm relative">
      <div className="grid grid-cols-2 gap-1 pb-3 border-b border-wfrp-border mb-3">
        <div className="font-display text-base col-span-1">{character.name}</div>
        <div className="text-right text-wfrp-muted text-xs col-span-1">{career?.name}</div>
      </div>

      {sessionMode === "COMBATE" && combatState ? (
        <div className="rounded border border-wfrp-combat/50 bg-wfrp-combat/20 p-2 text-xs mb-3">
          <div className="font-display text-blue-300">
            {t("session.combat")} — Turno {combatState.turn}
          </div>
          <div className="text-wfrp-muted mt-1">
            Ativo: {combatState.order[combatState.current_index]?.nome}
          </div>
        </div>
      ) : timeRemaining !== undefined ? (
        <div className="text-xs text-wfrp-muted mb-3">
          {t("session.exploration")} — {t("session.minutesRemaining", { count: timeRemaining })}
        </div>
      ) : null}

      <WoundsBar current={character.wounds_current} max={character.wounds_max} />
      <div className="flex justify-between items-center py-1">
        <span className="text-wfrp-muted">{t("character.fatePoints")}</span>
        <FateGems current={character.fate_current} max={character.fate_max} />
      </div>
      <div className="flex justify-between items-center py-1 mb-2">
        <span className="text-wfrp-muted">{t("character.fortunePoints")}</span>
        <FateGems current={character.fortune_current} max={character.fortune_max} />
      </div>

      <div className="sheet-section-label">{t("character.attributes")}</div>
      <AttributeCards
        attributes={character.attributes}
        disabled={quickRollDisabled}
        onSelect={(key, value) =>
          setPopover({ type: "attribute", key, label: key, target: value })
        }
      />

      <CollapsibleSection title={t("character.skills")} defaultOpen>
        <div className="skill-row-header" aria-hidden="true">
          <span>{t("character.skillColName")}</span>
          <span className="text-right">{t("character.skillColAttribute")}</span>
          <span className="text-right">{t("character.skillColAdvances")}</span>
          <span className="text-right">{t("character.skillColTarget")}</span>
        </div>
        {skillCatalog.map((s) => {
          const advances = ownedAdvances[s.name] ?? 0;
          const target = computeSkillTarget(
            character.attributes,
            s.name,
            skillCatalog,
            character.skills
          );
          return (
            <button
              key={s.name}
              type="button"
              className="skill-row rollable w-full text-xs py-0.5 disabled:opacity-40"
              disabled={quickRollDisabled}
              aria-label={`${s.name}, ${s.linked_attribute}, ${advances} avanços, alvo ${target}`}
              onClick={() =>
                setPopover({ type: "skill", key: s.name, label: s.name, target })
              }
            >
              <span className="skill-row-name">
                <TruncatedText>{s.name}</TruncatedText>
                <span className="skill-row-leader" aria-hidden="true" />
              </span>
              <span className="skill-row-attr">{s.linked_attribute}</span>
              <span className="skill-row-adv">{advances}</span>
              <span className="skill-row-target">{target}</span>
            </button>
          );
        })}
      </CollapsibleSection>

      <CollapsibleSection title={t("character.inventory")}>
        {character.trappings.map((item) => (
          <div key={item.name} className="flex items-center gap-2 py-0.5">
            {item.image_url && (
              <img
                src={item.image_url}
                alt=""
                className="w-8 h-8 rounded object-cover border border-wfrp-border shrink-0"
              />
            )}
            <button
              type="button"
              className="rollable flex-1 flex justify-between text-xs disabled:opacity-40"
              disabled={quickRollDisabled}
              onClick={() =>
                setPopover({
                  type: "weapon",
                  key: item.name,
                  label: item.name,
                  target: character.attributes.WS ?? 30,
                })
              }
            >
              <span>{item.name}</span>
            </button>
          </div>
        ))}
      </CollapsibleSection>

      {popover && (
        <QuickRollPopover
          target={popover}
          onRoll={async (mod) => {
            await onQuickRoll(popover, mod);
            setPopover(null);
          }}
          onCancel={() => setPopover(null)}
        />
      )}
    </div>
  );
}
