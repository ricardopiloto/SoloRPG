"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { RequireAuth } from "@/contexts/AuthContext";
import { api, Campaign, Character } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function CampaignsPage() {
  const router = useRouter();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedChar, setSelectedChar] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    Promise.all([api.listCharacters(), api.listCampaigns()])
      .then(([c, camp]) => {
        const alive = c.filter((ch) => ch.status === "vivo");
        setCharacters(alive);
        setCampaigns(camp);
        if (alive[0]) setSelectedChar(alive[0].id);
      })
      .catch((e) => {
        setLoadError(e instanceof Error ? e.message : "Não foi possível carregar campanhas.");
      });
  }, []);

  async function resumeOrStart(campaign: Campaign) {
    setLoading(true);
    setError("");
    try {
      if (campaign.active_session_id) {
        // Navigate to the existing session (hook will auto-resume if paused)
        router.push(`/play/${campaign.active_session_id}`);
        return;
      }
      const s = await api.startSession(campaign.id);
      router.push(`/play/${s.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível continuar a campanha.");
    } finally {
      setLoading(false);
    }
  }

  async function newCampaign() {
    if (!selectedChar) return;
    setLoading(true);
    setError("");
    try {
      const c = await api.createCampaign(selectedChar);
      const s = await api.startSession(c.id);
      router.push(`/play/${s.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível criar campanha.");
    } finally {
      setLoading(false);
    }
  }

  const active = campaigns.filter((c) => c.status === "ativa");
  const aliveWithoutActive = characters.filter(
    (ch) => !active.some((c) => c.character_id === ch.id)
  );

  return (
    <RequireAuth>
    <AppShell>
      <div className="container-wfrp py-12 max-w-2xl">
        <h1 className="font-display text-3xl mb-8">{t("nav.campaigns")}</h1>

        {(loadError || error) && (
          <p className="text-wfrp-danger text-sm mb-4">
            {loadError || error} — verifique se o backend está rodando.
          </p>
        )}

        {!loadError && characters.length === 0 ? (
          <p className="text-wfrp-muted mb-4">
            Crie um personagem primeiro.{" "}
            <Link href="/character" className="text-wfrp-accent underline">
              Personagens
            </Link>
          </p>
        ) : !loadError ? (
          <section className="card-wfrp mb-8 space-y-4">
            <h2 className="font-display text-lg">Nova campanha</h2>
            <p className="text-xs text-wfrp-muted">
              Escolha um personagem vivo sem campanha ativa, ou crie um novo personagem.
            </p>
            {aliveWithoutActive.length > 0 ? (
              <>
                <select
                  className="w-full bg-wfrp-bg border border-wfrp-border rounded px-3 py-2"
                  value={selectedChar}
                  onChange={(e) => setSelectedChar(e.target.value)}
                >
                  {aliveWithoutActive.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
                <button type="button" className="btn-primary" onClick={newCampaign} disabled={loading}>
                  Iniciar sessão (~45 min)
                </button>
              </>
            ) : (
              <p className="text-sm text-wfrp-muted">
                Todos os personagens vivos já têm campanha ativa.{" "}
                <Link href="/character" className="text-wfrp-accent underline">
                  Criar novo personagem
                </Link>
              </p>
            )}
          </section>
        ) : null}

        {!loadError && active.length > 0 && (
          <section className="mb-8">
            <h2 className="font-display text-lg mb-3">Continuar</h2>
            {active.map((c) => (
              <div key={c.id} className="card-wfrp mb-2 flex justify-between items-center gap-3">
                <div>
                  <span className="block">
                    {c.character_name} — {c.tone || c.opening_location || "ativa"}
                  </span>
                  {c.active_session_id && (
                    <span className="flex items-center gap-2 mt-1">
                      {c.active_session_paused ? (
                        <>
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-widest bg-wfrp-surface border border-wfrp-accent/40 text-wfrp-accent rounded">
                            ⏸ Pausada
                          </span>
                          {c.active_session_time_remaining != null && (
                            <span className="text-xs text-wfrp-muted">
                              {c.active_session_time_remaining} min restantes
                            </span>
                          )}
                        </>
                      ) : (
                        <span className="text-xs text-wfrp-accent">Sessão em andamento</span>
                      )}
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  className="btn-secondary text-sm shrink-0"
                  onClick={() => resumeOrStart(c)}
                  disabled={loading}
                >
                  {c.active_session_paused
                    ? "Retomar sessão"
                    : c.active_session_id
                    ? t("home.resume")
                    : t("home.continue")}
                </button>
              </div>
            ))}
          </section>
        )}

        {!loadError && (
        <section>
          <h2 className="font-display text-lg mb-3">{t("home.history")}</h2>
          {campaigns.map((c) => (
            <div key={c.id} className="text-sm py-2 border-b border-wfrp-border text-wfrp-muted flex justify-between">
              <span>
                {c.character_name} — {c.status}
              </span>
              {c.status === "concluida" && (
                <span className="tag">concluída</span>
              )}
            </div>
          ))}
        </section>
        )}
      </div>
    </AppShell>
    </RequireAuth>
  );
}
