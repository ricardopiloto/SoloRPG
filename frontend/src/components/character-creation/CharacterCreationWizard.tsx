"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AttributeCards } from "@/components/character/AttributeCards";
import { api } from "@/lib/api";
import {
  ATTRS,
  INITIAL_DRAFT,
  WIZARD_STEPS,
  type CareerDetail,
  type CharacterCreationDraft,
  type CreationPreview,
  type WizardStep,
} from "@/lib/character-creation";
import { t } from "@/lib/i18n";

const STORAGE_KEY = "wfrp-chargen-draft";

function stepLabel(step: WizardStep): string {
  return t(`chargen.steps.${step}`);
}

export function CharacterCreationWizard() {
  const router = useRouter();
  const [stepIdx, setStepIdx] = useState(0);
  const [draft, setDraft] = useState<CharacterCreationDraft>(INITIAL_DRAFT);
  const [careers, setCareers] = useState<Array<{ id: string; name: string }>>([]);
  const [careerDetail, setCareerDetail] = useState<CareerDetail | null>(null);
  const [speciesSkills, setSpeciesSkills] = useState<string[]>([]);
  const [preview, setPreview] = useState<CreationPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [swapA, setSwapA] = useState<string | null>(null);
  const [bgHints, setBgHints] = useState("");
  const [bgLoading, setBgLoading] = useState(false);

  const step = WIZARD_STEPS[stepIdx];

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        setDraft({ ...INITIAL_DRAFT, ...JSON.parse(raw) });
      } catch {
        /* ignore */
      }
    }
    api.getCreationOptions().then((r) => {
      const species = (r.options.species as Array<{ skills: string[] }>)?.[0];
      if (species?.skills) setSpeciesSkills(species.skills);
    });
    api.listCareers().then((r) => setCareers(r.careers));
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
  }, [draft]);

  useEffect(() => {
    if (!draft.career_id) {
      setCareerDetail(null);
      return;
    }
    api.getCareer(draft.career_id).then(setCareerDetail).catch(console.error);
  }, [draft.career_id]);

  const refreshPreview = useCallback(async (d: CharacterCreationDraft) => {
    if (!d.career_id) return;
    try {
      const res = await api.validateCreation(d);
      setPreview(res.computed);
    } catch {
      setPreview(null);
    }
  }, []);

  useEffect(() => {
    if (draft.career_id) refreshPreview(draft);
  }, [draft, refreshPreview]);

  const updateDraft = (patch: Partial<CharacterCreationDraft>) => {
    setDraft((prev) => ({ ...prev, ...patch }));
  };

  const canNext = useMemo(() => {
    if (step === "species") return true;
    if (step === "career") return !!draft.career_id;
    if (step === "attributes") {
      if (draft.attributes_method === "allocate") {
        const spent = ATTRS.reduce((s, a) => s + (draft.attribute_allocated[a] || 0), 0);
        return spent > 0 && spent <= 100;
      }
      return Object.keys(draft.attribute_rolls).length === 10;
    }
    if (step === "skills") {
      const total = Object.values(draft.career_skills).reduce((s, v) => s + v, 0);
      return total <= 40 && !!draft.career_talent;
    }
    if (step === "details") return draft.name.trim().length > 0;
    return true;
  }, [step, draft]);

  async function rollAttributes() {
    setLoading(true);
    setError("");
    try {
      const { attributes } = await api.rollCreationAttributes();
      updateDraft({
        attribute_rolls: attributes,
        attributes_rerolled: false,
        attributes_swapped: false,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao rolar atributos");
    } finally {
      setLoading(false);
    }
  }

  async function rerollAttributes() {
    await rollAttributes();
    updateDraft({ attributes_rerolled: true, attributes_swapped: false });
  }

  function swapAttribute(attr: string) {
    if (!swapA) {
      setSwapA(attr);
      return;
    }
    if (swapA === attr) {
      setSwapA(null);
      return;
    }
    const rolls = { ...draft.attribute_rolls };
    rolls[swapA] = draft.attribute_rolls[attr];
    rolls[attr] = draft.attribute_rolls[swapA];
    updateDraft({ attribute_rolls: rolls, attributes_swapped: true });
    setSwapA(null);
  }

  async function rollCareer() {
    setLoading(true);
    setError("");
    try {
      const res = await api.rollCreationCareer(draft);
      updateDraft({
        career_id: res.career.id,
        career_method: "roll",
        career_roll_count: res.career_roll_count,
        career_roll_options: res.career_roll_options,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao rolar carreira");
    } finally {
      setLoading(false);
    }
  }

  async function ensureSpeciesTalent() {
    if (draft.species_talents.length) return;
    try {
      const res = await api.rollSpeciesTalent(draft);
      updateDraft({ species_talents: [res.talent] });
    } catch {
      /* optional */
    }
  }

  useEffect(() => {
    if (step === "skills") ensureSpeciesTalent();
  }, [step]);

  async function generateBackground() {
    if (!draft.name.trim() || !careerDetail) return;
    setBgLoading(true);
    setError("");
    try {
      const skillsSummary = preview?.skills
        .filter((s) => s.advances > 0)
        .slice(0, 8)
        .map((s) => `${s.name} +${s.advances}`)
        .join(", ");
      const res = await api.generateBackground({
        name: draft.name.trim(),
        career: careerDetail.name,
        species: "Humano",
        talents: [
          ...draft.species_talents,
          ...(draft.career_talent ? [draft.career_talent] : []),
        ],
        skills_summary: skillsSummary,
        trappings: careerDetail.trappings.map((t) => t.name),
        hints: bgHints.trim() || undefined,
      });
      updateDraft({ background: res.background });
    } catch (e) {
      setError(e instanceof Error ? e.message : t("chargen.backgroundError"));
    } finally {
      setBgLoading(false);
    }
  }

  async function submit() {
    setLoading(true);
    setError("");
    try {
      await api.createCharacterFromDraft(draft);
      localStorage.removeItem(STORAGE_KEY);
      router.push("/campaigns");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível criar o personagem");
    } finally {
      setLoading(false);
    }
  }

  const displayAttrs =
    preview?.attributes ||
    (draft.attributes_method === "allocate"
      ? Object.fromEntries(
          ATTRS.map((a) => [a, (draft.attribute_allocated[a] || 0) + 20])
        )
      : draft.attribute_rolls);

  return (
    <div className="card-wfrp space-y-6">
      <div className="flex flex-wrap gap-2 text-xs">
        {WIZARD_STEPS.map((s, i) => (
          <span
            key={s}
            className={`px-2 py-1 rounded border ${i === stepIdx ? "border-wfrp-accent text-wfrp-fg" : "border-wfrp-border text-wfrp-muted"}`}
          >
            {i + 1}. {stepLabel(s)}
          </span>
        ))}
      </div>

      {error && <p className="text-wfrp-danger text-sm">{error}</p>}

      {step === "species" && (
        <div className="space-y-4">
          <p className="text-sm text-wfrp-muted">{t("chargen.speciesLead")}</p>
          <div className="flex gap-2">
            <button
              type="button"
              className={`tab-btn ${draft.species_method === "choose" ? "is-active" : ""}`}
              onClick={() => updateDraft({ species_id: "human", species_method: "choose" })}
            >
              {t("chargen.chooseSpecies")}
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={loading}
              onClick={() => updateDraft({ species_id: "human", species_method: "roll" })}
            >
              {t("chargen.rollSpecies")}
            </button>
          </div>
          <p className="text-sm font-medium">Humano (Reikland)</p>
        </div>
      )}

      {step === "career" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <button type="button" className="btn-secondary" disabled={loading} onClick={rollCareer}>
              {t("chargen.rollCareer")}
            </button>
          </div>
          {draft.career_roll_options.length > 0 && (
            <p className="text-xs text-wfrp-muted">
              {t("chargen.rolledCareers")}:{" "}
              {draft.career_roll_options.map((id) => careers.find((c) => c.id === id)?.name || id).join(", ")}
            </p>
          )}
          <div className="grid sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
            {careers.map((c) => (
              <button
                key={c.id}
                type="button"
                className={`text-left px-3 py-2 rounded border text-sm ${draft.career_id === c.id ? "border-wfrp-accent" : "border-wfrp-border"}`}
                onClick={() => updateDraft({ career_id: c.id, career_method: "choose" })}
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === "attributes" && (
        <div className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            <button
              type="button"
              className={`tab-btn ${draft.attributes_method === "roll" ? "is-active" : ""}`}
              onClick={() => updateDraft({ attributes_method: "roll" })}
            >
              {t("chargen.rollAttributes")}
            </button>
            <button
              type="button"
              className={`tab-btn ${draft.attributes_method === "allocate" ? "is-active" : ""}`}
              onClick={() => updateDraft({ attributes_method: "allocate" })}
            >
              {t("chargen.pointBuy")}
            </button>
          </div>

          {draft.attributes_method === "roll" ? (
            <>
              <div className="flex gap-2 flex-wrap">
                <button type="button" className="btn-secondary" disabled={loading} onClick={rollAttributes}>
                  {t("chargen.rollNow")}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  disabled={loading || !Object.keys(draft.attribute_rolls).length}
                  onClick={rerollAttributes}
                >
                  {t("chargen.rerollAll")}
                </button>
              </div>
              <p className="text-xs text-wfrp-muted">{t("chargen.swapHint")}</p>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {ATTRS.map((a) => (
                  <button
                    key={a}
                    type="button"
                    className={`border rounded px-2 py-2 text-sm ${swapA === a ? "border-wfrp-accent" : "border-wfrp-border"}`}
                    onClick={() => swapAttribute(a)}
                  >
                    <div className="text-wfrp-muted text-xs">{a}</div>
                    <div className="font-mono">{draft.attribute_rolls[a] ?? "—"}</div>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
              {ATTRS.map((a) => (
                <label key={a} className="text-xs text-wfrp-muted">
                  {a}
                  <input
                    type="number"
                    min={4}
                    max={18}
                    className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-2 py-1"
                    value={draft.attribute_allocated[a] || ""}
                    onChange={(e) =>
                      updateDraft({
                        attribute_allocated: {
                          ...draft.attribute_allocated,
                          [a]: Number(e.target.value) || 0,
                        },
                      })
                    }
                  />
                </label>
              ))}
            </div>
          )}

          <label className="block text-sm text-wfrp-muted">
            {t("character.fatePoints")} ({t("chargen.fatePool")})
            <input
              type="number"
              min={0}
              max={2}
              className="mt-1 w-24 bg-wfrp-bg border border-wfrp-border rounded px-2 py-1"
              value={draft.fate_allotted}
              onChange={(e) => updateDraft({ fate_allotted: Number(e.target.value) || 0 })}
            />
          </label>
        </div>
      )}

      {step === "skills" && careerDetail && (
        <div className="space-y-6">
          <div>
            <div className="sheet-section-label mb-2">{t("chargen.speciesSkills")}</div>
            <div className="space-y-1">
              {speciesSkills.map((skill) => (
                <div key={skill} className="flex items-center gap-2 text-sm">
                  <span className="flex-1">{skill}</span>
                  {[0, 3, 5].map((adv) => (
                    <button
                      key={adv}
                      type="button"
                      className={`px-2 py-0.5 rounded text-xs border ${draft.species_skills[skill] === adv ? "border-wfrp-accent" : "border-wfrp-border"}`}
                      onClick={() =>
                        updateDraft({
                          species_skills: { ...draft.species_skills, [skill]: adv },
                        })
                      }
                    >
                      +{adv}
                    </button>
                  ))}
                </div>
              ))}
            </div>
            {draft.species_talents[0] && (
              <p className="text-xs text-wfrp-muted mt-2">
                {t("chargen.speciesTalent")}: {draft.species_talents[0]}
              </p>
            )}
          </div>

          <div>
            <div className="sheet-section-label mb-2">{t("chargen.careerSkills")}</div>
            <p className="text-xs text-wfrp-muted mb-2">
              {t("chargen.careerPoints")}:{" "}
              {Object.values(draft.career_skills).reduce((s, v) => s + v, 0)} / 40
            </p>
            <div className="grid sm:grid-cols-2 gap-2">
              {careerDetail.skills.map((skill) => (
                <label key={skill} className="text-xs flex items-center gap-2">
                  <span className="flex-1 truncate">{skill}</span>
                  <input
                    type="number"
                    min={0}
                    max={10}
                    className="w-14 bg-wfrp-bg border border-wfrp-border rounded px-1 py-0.5"
                    value={draft.career_skills[skill] || ""}
                    onChange={(e) =>
                      updateDraft({
                        career_skills: {
                          ...draft.career_skills,
                          [skill]: Math.min(10, Math.max(0, Number(e.target.value) || 0)),
                        },
                      })
                    }
                  />
                </label>
              ))}
            </div>
          </div>

          <div>
            <div className="sheet-section-label mb-2">{t("chargen.careerTalent")}</div>
            <div className="flex flex-wrap gap-2">
              {careerDetail.talents.map((talent) => (
                <button
                  key={talent}
                  type="button"
                  className={`px-3 py-1 rounded border text-sm ${draft.career_talent === talent ? "border-wfrp-accent" : "border-wfrp-border"}`}
                  onClick={() => updateDraft({ career_talent: talent })}
                >
                  {talent}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {step === "trappings" && careerDetail && (
        <div className="space-y-2 text-sm">
          <p className="text-wfrp-muted">{t("chargen.trappingsLead")}</p>
          <ul className="list-disc pl-5 space-y-1">
            {careerDetail.trappings.map((tr) => (
              <li key={tr.name}>{tr.name}</li>
            ))}
            <li>Bolsa de moedas (50 coroas imperiais)</li>
          </ul>
        </div>
      )}

      {step === "details" && (
        <div className="space-y-4">
          <label className="block text-sm">
            {t("chargen.name")}
            <input
              className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2"
              value={draft.name}
              onChange={(e) => updateDraft({ name: e.target.value })}
              required
            />
          </label>
          <label className="block text-sm">
            {t("chargen.backgroundHints")}
            <input
              className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2 text-sm"
              value={bgHints}
              onChange={(e) => setBgHints(e.target.value)}
              placeholder={t("chargen.backgroundHintsPlaceholder")}
            />
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              className="btn-secondary"
              disabled={bgLoading || !draft.name.trim() || !careerDetail}
              onClick={generateBackground}
            >
              {bgLoading ? t("chargen.generating") : t("chargen.generateBackground")}
            </button>
          </div>
          <label className="block text-sm">
            Background
            <textarea
              className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2 min-h-[120px]"
              value={draft.background || ""}
              onChange={(e) => updateDraft({ background: e.target.value })}
            />
          </label>

          {preview && (
            <div className="border-t border-wfrp-border pt-4 space-y-3">
              <div className="sheet-section-label">{t("chargen.review")}</div>
              <p className="text-sm text-wfrp-muted">
                {careerDetail?.name} · {t("character.wounds")} {preview.wounds_max} · {t("character.fatePoints")}{" "}
                {preview.fate_max} · XP {preview.xp_total}
              </p>
              <AttributeCards
                attributes={displayAttrs}
                disabled
                onSelect={() => {}}
              />
            </div>
          )}
        </div>
      )}

      <div className="flex justify-between pt-2 border-t border-wfrp-border">
        <button
          type="button"
          className="btn-secondary"
          disabled={stepIdx === 0 || loading}
          onClick={() => setStepIdx((i) => Math.max(0, i - 1))}
        >
          {t("chargen.back")}
        </button>
        {stepIdx < WIZARD_STEPS.length - 1 ? (
          <button
            type="button"
            className="btn-primary"
            disabled={!canNext || loading}
            onClick={() => setStepIdx((i) => i + 1)}
          >
            {t("chargen.next")}
          </button>
        ) : (
          <button type="button" className="btn-primary" disabled={!canNext || loading} onClick={submit}>
            {t("chargen.confirm")}
          </button>
        )}
      </div>
    </div>
  );
}
