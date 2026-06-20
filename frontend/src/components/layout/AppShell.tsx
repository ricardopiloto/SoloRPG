import Link from "next/link";
import { t } from "@/lib/i18n";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh flex flex-col">
      <header className="topnav">
        <div className="container-wfrp topnav-inner">
          <Link href="/" className="logo">
            {t("app.title")}
          </Link>
          <nav className="hidden sm:flex gap-6 text-sm text-wfrp-muted">
            <Link href="/character" className="hover:text-wfrp-fg">
              {t("nav.characters")}
            </Link>
            <Link href="/campaigns" className="hover:text-wfrp-fg">
              {t("nav.campaigns")}
            </Link>
          </nav>
          <Link href="/campaigns" className="btn-primary text-sm py-1.5">
            {t("nav.newCampaign")}
          </Link>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
