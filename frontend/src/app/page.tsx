"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { api, Campaign, Character } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function HomePage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    Promise.all([api.listCharacters(), api.listCampaigns()])
      .then(([c, camp]) => {
        setCharacters(c);
        setCampaigns(camp);
      })
      .catch((e) => {
        setLoadError(e instanceof Error ? e.message : "Não foi possível carregar dados.");
      });
  }, []);

  const active = campaigns.find((c) => c.status === "ativa");
  const hero = active?.character_name || characters[0]?.name;

  return (
    <AppShell>
      <div className="container-wfrp py-12">
        {loadError && (
          <p className="text-wfrp-danger text-sm mb-4">
            {loadError} — verifique se o backend está rodando em{" "}
            {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}.
          </p>
        )}
        {characters.length === 0 ? (
          <section className="text-center py-16">
            <p className="eyebrow">{t("home.emptyTitle")}</p>
            <h1 className="font-display text-3xl mb-4">WFRP Solo</h1>
            <p className="text-wfrp-muted max-w-lg mx-auto mb-8">{t("home.emptyLead")}</p>
            <Link href="/character" className="btn-primary">
              {t("home.newCharacter")}
            </Link>
          </section>
        ) : (
          <>
            <section className="mb-12">
              <p className="eyebrow">{t("home.welcome")}</p>
              <h1 className="font-display text-3xl mb-2">Olá, {hero}</h1>
              <p className="text-wfrp-muted max-w-2xl">
                {active
                  ? `${active.tone || "Campanha"} · ${active.opening_location || "Em andamento"}`
                  : "Crie uma nova campanha para começar."}
              </p>
              <div className="flex flex-wrap gap-3 mt-6">
                {active && (
                  <Link
                    href={
                      active.active_session_id
                        ? `/play/${active.active_session_id}`
                        : "/campaigns"
                    }
                    className="btn-primary"
                  >
                    {active.active_session_id ? t("home.resume") : t("home.resume")}
                  </Link>
                )}
                <Link href="/campaigns" className="btn-secondary">
                  {t("nav.campaigns")}
                </Link>
                <Link href="/character" className="btn-ghost">
                  {t("nav.characters")}
                </Link>
              </div>
            </section>

            {active && (
              <section className="mb-12">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="font-display text-xl">{t("home.activeCampaign")}</h2>
                  <span className="pill">{t("session.exploration")}</span>
                </div>
                <div className="card-wfrp">
                  <div className="flex justify-between gap-4 flex-wrap">
                    <div>
                      <h3 className="font-display text-lg mb-1">{active.tone || "Campanha ativa"}</h3>
                      <p className="text-wfrp-muted text-sm">{active.opening_location}</p>
                      <span className="tag tag-active mt-2 inline-block">{active.status}</span>
                    </div>
                    <Link
                      href={
                        active.active_session_id
                          ? `/play/${active.active_session_id}`
                          : "/campaigns"
                      }
                      className="btn-primary text-sm self-start"
                    >
                      {active.active_session_id ? t("home.resume") : t("home.continue")}
                    </Link>
                  </div>
                </div>
              </section>
            )}

            {campaigns.length > 0 && (
              <section>
                <h2 className="font-display text-xl mb-4">{t("home.history")}</h2>
                <div className="space-y-2">
                  {campaigns.map((c) => (
                    <div key={c.id} className="card-wfrp text-sm flex justify-between">
                      <span>
                        <strong>{c.character_name}</strong> — {c.status}
                        {c.tone && <span className="text-wfrp-muted"> · {c.tone}</span>}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
