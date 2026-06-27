"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { api, Character, ProgressionOptions } from "@/lib/api";
import { t } from "@/lib/i18n";

function purchaseLabel(purchase: ProgressionOptions["refundable_purchases"][number]): string {
  if (purchase.type === "skill" && purchase.skill_name) {
    return `${purchase.skill_name} +1 (${purchase.linked_attribute ?? "?"})`;
  }
  if (purchase.type === "talent" && purchase.talent_name) {
    return purchase.talent_name;
  }
  return purchase.type;
}

export default function ProgressionPage() {
  const [character, setCharacter] = useState<Character | null>(null);
  const [options, setOptions] = useState<ProgressionOptions | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (characterId: string) => {
    const [char, opts] = await Promise.all([
      api.getCharacter(characterId),
      api.getProgressionOptions(characterId),
    ]);
    setCharacter(char);
    setOptions(opts);
  }, []);

  useEffect(() => {
    const raw = sessionStorage.getItem("wfrp-recap");
    const recap = raw ? JSON.parse(raw) : null;
    const characterId = recap?.characterId as string | undefined;

    if (characterId) {
      load(characterId).catch(console.error);
      return;
    }
    api.listCharacters().then((chars) => {
      if (chars[0]) load(chars[0].id).catch(console.error);
    });
  }, [load]);

  async function buySkill(skillName: string, linkedAttribute: string) {
    if (!character) return;
    setLoading(true);
    try {
      const c = await api.buySkill(character.id, skillName, linkedAttribute);
      setCharacter(c);
      setOptions(await api.getProgressionOptions(c.id));
    } finally {
      setLoading(false);
    }
  }

  async function buyTalent(talentName: string) {
    if (!character) return;
    setLoading(true);
    try {
      const c = await api.buyTalent(character.id, talentName);
      setCharacter(c);
      setOptions(await api.getProgressionOptions(c.id));
    } finally {
      setLoading(false);
    }
  }

  async function refundPurchase(purchaseId: string) {
    if (!character) return;
    setLoading(true);
    try {
      const c = await api.refundPurchase(character.id, purchaseId);
      setCharacter(c);
      setOptions(await api.getProgressionOptions(c.id));
    } finally {
      setLoading(false);
    }
  }

  if (!character || !options) {
    return (
      <AppShell>
        <div className="container-wfrp py-16 text-wfrp-muted">Carregando…</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="container-wfrp py-12 max-w-xl">
        <h1 className="font-display text-3xl mb-2">Progressão — {character.name}</h1>
        <p className="text-wfrp-muted mb-8">
          {t("character.xp")} disponível: <strong>{options.xp_available}</strong>
        </p>

        {options.progression_window_active && options.refundable_purchases.length > 0 && (
          <section className="mb-8">
            <h2 className="font-display text-lg mb-2">{t("progression.refundSection")}</h2>
            <p className="text-wfrp-muted text-sm mb-3">
              {t("progression.refundBudget", {
                remaining: options.refund_budget_remaining,
                total: options.refund_budget_total,
              })}
            </p>
            <div className="space-y-2">
              {options.refundable_purchases.map((purchase) => (
                <div
                  key={purchase.id}
                  className="card-wfrp flex items-center justify-between gap-3"
                >
                  <span>
                    {purchaseLabel(purchase)}
                    <span className="text-wfrp-muted text-sm ml-2">{purchase.cost} XP</span>
                  </span>
                  <button
                    type="button"
                    disabled={loading}
                    className="btn-ghost text-sm shrink-0"
                    onClick={() => refundPurchase(purchase.id)}
                  >
                    {t("progression.refund")}
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        <h2 className="font-display text-lg mb-3">{t("character.skills")}</h2>
        <div className="space-y-2 mb-8">
          {options.skills.map((skill) => (
            <button
              key={skill.name}
              type="button"
              disabled={!skill.affordable || loading}
              className="card-wfrp w-full text-left hover:border-wfrp-accent disabled:opacity-40"
              onClick={() => buySkill(skill.name, skill.linked_attribute)}
            >
              {skill.name} +1 ({skill.linked_attribute})
              <span className="text-wfrp-muted text-sm ml-2">
                {skill.cost} XP · atual +{skill.current_advances}
              </span>
            </button>
          ))}
        </div>

        <h2 className="font-display text-lg mb-3">{t("character.talents")}</h2>
        <div className="space-y-2">
          {options.talents.map((talent) => (
            <button
              key={talent.name}
              type="button"
              disabled={!talent.affordable || talent.owned || loading}
              className="card-wfrp w-full text-left hover:border-wfrp-accent disabled:opacity-40"
              onClick={() => buyTalent(talent.name)}
            >
              {talent.name}
              <span className="text-wfrp-muted text-sm ml-2">
                {talent.cost} XP
                {talent.owned && " · adquirido"}
              </span>
            </button>
          ))}
        </div>

        <Link href="/" className="btn-ghost mt-8 inline-block">
          Voltar
        </Link>
      </div>
    </AppShell>
  );
}
