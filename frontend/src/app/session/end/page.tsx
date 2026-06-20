"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { t } from "@/lib/i18n";

export default function SessionEndPage() {
  const [recap, setRecap] = useState<{ summary: string; xp: number } | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("wfrp-recap");
    if (raw) setRecap(JSON.parse(raw));
  }, []);

  if (!recap) {
    return (
      <AppShell>
        <div className="container-wfrp py-16 text-center text-wfrp-muted">
          Nenhum resumo de sessão.
          <Link href="/" className="block mt-4 text-wfrp-accent">
            Início
          </Link>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="container-wfrp py-16 max-w-2xl">
        <h1 className="font-display text-3xl mb-6 text-wfrp-accent">{t("end.title")}</h1>
        <div className="font-narrative text-lg leading-relaxed whitespace-pre-wrap mb-8">
          {recap.summary}
        </div>
        <p className="text-lg mb-8">
          {t("end.xpGained")}: <strong>{recap.xp}</strong>
        </p>
        <div className="flex gap-3">
          <Link href="/progression" className="btn-primary">
            {t("end.progression")}
          </Link>
          <Link href="/campaigns" className="btn-secondary">
            {t("end.continue")}
          </Link>
          <Link href="/" className="btn-ghost">
            Início
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
