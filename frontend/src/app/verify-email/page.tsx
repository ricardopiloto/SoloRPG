"use client";

import { Suspense } from "react";
import VerifyEmailForm from "./VerifyEmailForm";

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="container-wfrp py-16 text-center text-wfrp-muted">Carregando…</div>}>
      <VerifyEmailForm />
    </Suspense>
  );
}
