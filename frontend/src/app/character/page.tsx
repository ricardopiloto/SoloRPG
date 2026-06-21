"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

const ATTRS = ["WS", "BS", "S", "T", "I", "Ag", "Dex", "Int", "WP", "Fel"] as const;

const DEFAULT_ATTRS = Object.fromEntries(ATTRS.map((a) => [a, 30])) as Record<string, number>;

export default function CharacterPage() {
  const router = useRouter();
  const [pregens, setPregens] = useState<Array<{ index: number; name: string; background: string; career: string }>>([]);
  const [mode, setMode] = useState<"pregen" | "custom">("pregen");
  const [name, setName] = useState("");
  const [background, setBackground] = useState("");
  const [career, setCareer] = useState("");
  const [attributes, setAttributes] = useState<Record<string, number>>({ ...DEFAULT_ATTRS });
  const [woundsMax, setWoundsMax] = useState(10);
  const [fateMax, setFateMax] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    api.listPregen()
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

  async function createCustom(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError("");
    try {
      await api.createCharacter({
        name: name.trim(),
        background: background.trim() || undefined,
        attributes,
        wounds_max: woundsMax,
        fate_max: fateMax,
        careers: [{ name: career.trim() || "Aventureiro", tier: 1 }],
        skills: [],
        talents: [],
        trappings: [],
      });
      router.push("/campaigns");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível criar o personagem.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="container-wfrp py-12 max-w-3xl">
        <h1 className="font-display text-3xl mb-2">{t("nav.characters")}</h1>
        <p className="text-wfrp-muted mb-6">Escolha um pré-gerado ou crie do zero.</p>

        {(loadError || error) && (
          <p className="text-wfrp-danger text-sm mb-4">
            {loadError || error} — verifique se o backend está rodando.
          </p>
        )}

        <div className="flex gap-2 mb-8">
          <button
            type="button"
            className={`tab-btn ${mode === "pregen" ? "is-active" : ""}`}
            onClick={() => setMode("pregen")}
          >
            Pré-gerados
          </button>
          <button
            type="button"
            className={`tab-btn ${mode === "custom" ? "is-active" : ""}`}
            onClick={() => setMode("custom")}
          >
            Customizado
          </button>
        </div>

        {mode === "pregen" && (
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

        {mode === "custom" && (
          <form onSubmit={createCustom} className="card-wfrp space-y-6">
            <div className="grid sm:grid-cols-2 gap-4">
              <label className="block text-sm">
                Nome
                <input
                  className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </label>
              <label className="block text-sm">
                Carreira inicial
                <input
                  className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2"
                  value={career}
                  onChange={(e) => setCareer(e.target.value)}
                  placeholder="Ex.: Soldado"
                />
              </label>
            </div>
            <label className="block text-sm">
              Background
              <textarea
                className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2 min-h-[80px]"
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                placeholder="História breve do personagem"
              />
            </label>

            <div>
              <div className="sheet-section-label mb-2">{t("character.attributes")}</div>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {ATTRS.map((attr) => (
                  <label key={attr} className="text-xs text-wfrp-muted">
                    {attr}
                    <input
                      type="number"
                      min={10}
                      max={60}
                      className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-2 py-1 text-wfrp-fg"
                      value={attributes[attr]}
                      onChange={(e) =>
                        setAttributes((prev) => ({
                          ...prev,
                          [attr]: Math.min(60, Math.max(10, Number(e.target.value) || 30)),
                        }))
                      }
                    />
                  </label>
                ))}
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <label className="text-sm text-wfrp-muted">
                Ferimentos máx.
                <input
                  type="number"
                  min={5}
                  max={20}
                  className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2"
                  value={woundsMax}
                  onChange={(e) => setWoundsMax(Number(e.target.value) || 10)}
                />
              </label>
              <label className="text-sm text-wfrp-muted">
                Pontos de Destino
                <input
                  type="number"
                  min={1}
                  max={5}
                  className="mt-1 w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2"
                  value={fateMax}
                  onChange={(e) => setFateMax(Number(e.target.value) || 2)}
                />
              </label>
            </div>
            <p className="text-xs text-wfrp-muted">
              Pontos de Fortuna são iguais aos de Destino e renovam no início de cada sessão.
            </p>

            <button type="submit" className="btn-primary" disabled={loading || !name.trim()}>
              Criar e continuar
            </button>
          </form>
        )}
      </div>
    </AppShell>
  );
}
