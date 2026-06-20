import Link from "next/link";
import { t } from "@/lib/i18n";

export default function LandingPage() {
  return (
    <div className="min-h-dvh flex flex-col">
      <section className="flex-1 container-wfrp py-20 grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <p className="eyebrow">Warhammer Fantasy · Solo</p>
          <h1 className="font-display text-4xl lg:text-5xl leading-tight mb-6">
            {t("app.title")}
          </h1>
          <p className="text-lg text-wfrp-muted leading-relaxed mb-8 max-w-prose">
            {t("app.tagline")}
          </p>
          <div className="flex flex-wrap gap-3">
            <Link href="/character" className="btn-primary">
              {t("home.newCharacter")}
            </Link>
            <Link href="/" className="btn-secondary">
              Entrar
            </Link>
          </div>
        </div>
        <div className="card-wfrp p-8 border-wfrp-accent/30">
          <h2 className="font-display text-xl mb-4">Como funciona</h2>
          <ol className="space-y-3 text-wfrp-muted text-sm list-decimal list-inside">
            <li>Crie ou escolha um personagem WFRP4e</li>
            <li>Inicie uma campanha — o GM sintético narra</li>
            <li>Jogue em texto livre, sessões de ~45 min</li>
            <li>Progrida entre sessões com XP real</li>
          </ol>
        </div>
      </section>
    </div>
  );
}
