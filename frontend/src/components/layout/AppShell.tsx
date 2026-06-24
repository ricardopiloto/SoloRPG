"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { AudioMuteButton } from "@/components/audio/AudioMuteButton";
import { t } from "@/lib/i18n";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

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
          <div className="flex items-center gap-3">
            {user && (
              <span className="hidden md:inline text-xs text-wfrp-muted truncate max-w-[160px]">
                {user.email}
              </span>
            )}
            {user && <AudioMuteButton />}
            <button type="button" onClick={handleLogout} className="btn-ghost text-sm py-1.5">
              {t("auth.logout")}
            </button>
            <Link href="/campaigns" className="btn-primary text-sm py-1.5">
              {t("nav.newCampaign")}
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
