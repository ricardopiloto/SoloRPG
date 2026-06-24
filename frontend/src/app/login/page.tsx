"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { AudioMuteButton } from "@/components/audio/AudioMuteButton";
import { api, AuthConfig } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [authConfig, setAuthConfig] = useState<AuthConfig | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const passwordOnly = authConfig !== null && !authConfig.registration_enabled;

  useEffect(() => {
    api.getAuthConfig().then(setAuthConfig).catch(() => setAuthConfig(null));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const loginEmail = passwordOnly ? authConfig!.login_username : email;
    try {
      await login(loginEmail, password);
      router.push("/");
    } catch (err) {
      const msg = err instanceof Error ? err.message : t("auth.errorGeneric");
      if (msg.includes("verification_required") || msg.includes("Verifique")) {
        router.push(`/verify-email?email=${encodeURIComponent(loginEmail)}`);
        return;
      }
      setError(t("auth.errorLogin"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-dvh">
      <div className="absolute top-4 right-4 z-10">
        <AudioMuteButton />
      </div>
      <div className="container-wfrp py-16 max-w-md mx-auto">
      <p className="eyebrow">{t("auth.loginTitle")}</p>
      <h1 className="font-display text-3xl mb-6">{t("app.title")}</h1>
      {passwordOnly && (
        <p className="text-xs text-wfrp-muted mb-4">{t("auth.passwordOnly")}</p>
      )}
      <form onSubmit={onSubmit} className="space-y-4">
        {!passwordOnly && (
          <label className="block">
            <span className="text-sm text-wfrp-muted">{t("auth.email")}</span>
            <input
              type="text"
              inputMode="email"
              autoComplete="username"
              required
              className="input-wfrp mt-1 w-full"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
        )}
        <label className="block">
          <span className="text-sm text-wfrp-muted">{t("auth.password")}</span>
          <input
            type="password"
            required
            autoComplete="current-password"
            className="input-wfrp mt-1 w-full"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error && <p className="text-wfrp-danger text-sm">{error}</p>}
        <button type="submit" className="btn-primary w-full" disabled={loading || authConfig === null}>
          {loading ? t("auth.loading") : t("auth.login")}
        </button>
      </form>
      {authConfig?.registration_enabled && (
        <p className="text-sm text-wfrp-muted mt-6">
          {t("auth.noAccount")}{" "}
          <Link href="/register" className="text-wfrp-gold hover:underline">
            {t("auth.register")}
          </Link>
        </p>
      )}
    </div>
    </div>
  );
}
