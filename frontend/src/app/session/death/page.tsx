"use client";

import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { t } from "@/lib/i18n";

export default function SessionDeathPage() {
  return (
    <AppShell>
      <div className="container-wfrp py-16 max-w-2xl text-center">
        <h1 className="font-display text-3xl mb-4 text-wfrp-danger">{t("death.title")}</h1>
        <p className="text-wfrp-muted mb-2">{t("death.subtitle")}</p>
        <p className="font-narrative text-lg leading-relaxed my-8 text-wfrp-muted">
          O destino cobrou seu preço. A história deste personagem termina aqui — mas o Velho Mundo
          continua, implacável.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/character" className="btn-primary">
            {t("death.newCharacter")}
          </Link>
          <Link href="/campaigns" className="btn-secondary">
            {t("death.newCampaign")}
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
