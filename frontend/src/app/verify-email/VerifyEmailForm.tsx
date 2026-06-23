"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

export default function VerifyEmailForm() {
  const { verifyEmail, resendVerification } = useAuth();
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState(params.get("email") || "");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
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
    setLoading(true);
    try {
      await verifyEmail(email, code);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("auth.errorVerify"));
    } finally {
      setLoading(false);
    }
  }

  async function onResend() {
    setError("");
    setInfo("");
    try {
      await resendVerification(email);
      setInfo(t("auth.codeResent"));
    } catch (err) {
      setError(err instanceof Error ? err.message : t("auth.errorGeneric"));
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
      <p className="eyebrow">{t("auth.verifyTitle")}</p>
      <h1 className="font-display text-3xl mb-2">{t("auth.verifyHeading")}</h1>
      <p className="text-wfrp-muted mb-6">{t("auth.verifyLead")}</p>
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
          <span className="text-sm text-wfrp-muted">{t("auth.verificationCode")}</span>
          <input
            type="text"
            inputMode="numeric"
            pattern="\d{8}"
            maxLength={8}
            required
            placeholder="12345678"
            className="input-wfrp mt-1 w-full tracking-widest font-mono"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 8))}
          />
        </label>
        {error && <p className="text-wfrp-danger text-sm">{error}</p>}
        {info && <p className="text-green-700 text-sm">{info}</p>}
        <button type="submit" className="btn-primary w-full" disabled={loading || code.length !== 8}>
          {loading ? t("auth.loading") : t("auth.verifySubmit")}
        </button>
      </form>
      <button type="button" onClick={onResend} className="btn-ghost mt-4 w-full text-sm">
        {t("auth.resendCode")}
      </button>
      <p className="text-sm text-wfrp-muted mt-6">
        <Link href="/login" className="text-wfrp-gold hover:underline">
          {t("auth.backToLogin")}
        </Link>
      </p>
    </div>
  );
}
