"use client";

import { useEffect, useState } from "react";
import { api, ImageJob } from "@/lib/api";

export function SceneImage({
  jobId,
  imageType,
  initialUrl,
  initialStatus = "pending",
  onReady,
}: {
  jobId: string;
  imageType: string;
  initialUrl?: string;
  initialStatus?: string;
  onReady?: (job: ImageJob) => void;
}) {
  const [job, setJob] = useState<ImageJob>({
    id: jobId,
    status: initialStatus,
    image_type: imageType,
    image_url: initialUrl ?? null,
    placeholder_url: initialUrl ?? null,
  });

  useEffect(() => {
    if (job.status === "completed" || job.status === "failed") return;

    let cancelled = false;
    const poll = async () => {
      try {
        const next = await api.getImageJob(jobId);
        if (!cancelled) {
          setJob(next);
          if ((next.status === "completed" || next.status === "failed") && onReady) {
            onReady(next);
          }
        }
      } catch {
        /* retry on next interval */
      }
    };

    poll();
    const timer = setInterval(poll, 1500);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [jobId, job.status, onReady]);

  if (job.status === "failed") return null;

  const displayUrl = job.image_url || job.placeholder_url;
  const loading = job.status === "pending" || job.status === "processing";

  return (
    <figure className="scene-image" aria-busy={loading}>
      {loading && (
        <div className="scene-image-placeholder">
          <span className="scene-image-spinner" aria-hidden />
          <span className="text-xs uppercase tracking-widest text-wfrp-muted">
            Gerando ilustração…
          </span>
        </div>
      )}
      {displayUrl && (
        <img
          src={displayUrl}
          alt=""
          className={`scene-image-img ${loading ? "is-loading" : "is-ready"}`}
        />
      )}
    </figure>
  );
}
