"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api
      .getAuthConfig()
      .then((config) => {
        if (!config.registration_enabled) {
          router.replace("/login");
          return;
        }
        setReady(true);
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (password !== passwordConfirm) {
      setError(t("auth.passwordMismatch"));
      return;
    }
    setLoading(true);
    try {
      await register(email, password, passwordConfirm);
      router.push(`/verify-email?email=${encodeURIComponent(email)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("auth.errorGeneric"));
    } finally {
      setLoading(false);
    }
  }

  if (!ready) {
    return (
      <div className="container-wfrp py-16 text-center text-wfrp-muted">
        {t("auth.loading")}
      </div>
    );
  }

  return (
    <div className="container-wfrp py-16 max-w-md mx-auto">
      <p className="eyebrow">{t("auth.registerTitle")}</p>
      <h1 className="font-display text-3xl mb-6">{t("auth.createAccount")}</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <label className="block">
          <span className="text-sm text-wfrp-muted">{t("auth.email")}</span>
          <input
            type="email"
            required
            className="input-wfrp mt-1 w-full"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm text-wfrp-muted">{t("auth.password")}</span>
          <input
            type="password"
            required
            minLength={8}
            className="input-wfrp mt-1 w-full"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm text-wfrp-muted">{t("auth.passwordConfirm")}</span>
          <input
            type="password"
            required
            minLength={8}
            className="input-wfrp mt-1 w-full"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
          />
        </label>
        {error && <p className="text-wfrp-danger text-sm">{error}</p>}
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? t("auth.loading") : t("auth.register")}
        </button>
      </form>
      <p className="text-sm text-wfrp-muted mt-6">
        {t("auth.hasAccount")}{" "}
        <Link href="/login" className="text-wfrp-gold hover:underline">
          {t("auth.login")}
        </Link>
      </p>
    </div>
  );
}
