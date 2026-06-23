"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { RequireAuth } from "@/contexts/AuthContext";
import { customChargenEnabled } from "@/lib/env";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

const CharacterCreationWizard = dynamic(
  () =>
    import("@/components/character-creation/CharacterCreationWizard").then(
      (m) => m.CharacterCreationWizard
    ),
  { ssr: false }
);

export default function CharacterPage() {
  const router = useRouter();
  const [pregens, setPregens] = useState<
    Array<{ index: number; name: string; background: string; career: string }>
  >([]);
  const [mode, setMode] = useState<"pregen" | "wizard">("pregen");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    api
      .listPregen()
      .then(setPregens)
      .catch((e) => {
        setLoadError(e instanceof Error ? e.message : "Não foi possível carregar pré-gerados.");
      });
  }, []);

  async function selectPregen(index: number) {
    setLoading(true);
    setError("");
    try {
      await api.createPregen(index);
      router.push("/campaigns");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível criar o personagem.");
    } finally {
      setLoading(false);
    }
  }

  const showWizard = customChargenEnabled && mode === "wizard";

  return (
    <RequireAuth>
      <AppShell>
        <div className="container-wfrp py-12 max-w-3xl">
          <h1 className="font-display text-3xl mb-2">{t("nav.characters")}</h1>
          <p className="text-wfrp-muted mb-6">
            {customChargenEnabled ? t("chargen.pageLead") : t("chargen.pageLeadPregenOnly")}
          </p>

          {(loadError || error) && (
            <p className="text-wfrp-danger text-sm mb-4">
              {loadError || error} — verifique se o backend está rodando.
            </p>
          )}

          {customChargenEnabled && (
            <div className="flex gap-2 mb-8">
              <button
                type="button"
                className={`tab-btn ${mode === "pregen" ? "is-active" : ""}`}
                onClick={() => setMode("pregen")}
              >
                {t("chargen.pregenTab")}
              </button>
              <button
                type="button"
                className={`tab-btn ${mode === "wizard" ? "is-active" : ""}`}
                onClick={() => setMode("wizard")}
              >
                {t("chargen.wizardTab")}
              </button>
            </div>
          )}

          {(mode === "pregen" || !customChargenEnabled) && (
            <div className="grid sm:grid-cols-2 gap-3">
              {pregens.map((p) => (
                <button
                  key={p.index}
                  type="button"
                  disabled={loading}
                  className="card-wfrp text-left hover:border-wfrp-accent transition-colors"
                  onClick={() => selectPregen(p.index)}
                >
                  <div className="font-medium">{p.name}</div>
                  <div className="text-xs text-wfrp-muted mt-1">
                    {p.career} — {p.background}
                  </div>
                </button>
              ))}
            </div>
          )}

          {showWizard && <CharacterCreationWizard />}
        </div>
      </AppShell>
    </RequireAuth>
  );
}
