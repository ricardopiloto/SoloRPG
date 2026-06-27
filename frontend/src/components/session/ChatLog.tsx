"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import { MarkdownNarrative } from "./MarkdownNarrative";
import { SceneImage } from "./SceneImage";
import type { ImageJob } from "@/lib/api";
import { t } from "@/lib/i18n";

export type ChatEntry =
  | { kind: "narrative"; content: string; streaming?: boolean }
  | { kind: "player"; content: string }
  | { kind: "roll"; content: string; success?: boolean }
  | {
      kind: "image";
      jobId: string;
      imageType: string;
      url?: string;
      status?: string;
    }
  | {
      kind: "dice-roll";
      rollId: string;
      label: string;
      meta: string;
      target?: number;
    }
  | {
      kind: "session-end";
      xp: number;
      playerSummary?: string;
      campaignId?: string;
      characterId?: string;
    };

type AttributionKind = "narrative" | "player" | "other";

function attributionKind(entry: ChatEntry): AttributionKind {
  if (entry.kind === "narrative") return "narrative";
  if (entry.kind === "player") return "player";
  return "other";
}

function isGroupStart(entries: ChatEntry[], index: number): boolean {
  if (index === 0) return true;
  const cur = attributionKind(entries[index]);
  if (cur === "other") return false;
  // Walk backwards past "other" kinds to find the last authored entry
  for (let i = index - 1; i >= 0; i--) {
    const prev = attributionKind(entries[i]);
    if (prev !== "other") return prev !== cur;
  }
  return true;
}

export function ChatLog({
  entries,
  preparing,
  onImageReady,
}: {
  entries: ChatEntry[];
  preparing?: boolean;
  onImageReady?: (job: ImageJob) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const diceActive = entries.some((e) => e.kind === "dice-roll");

    // While DiceOverlay is visible it covers the entire chat area — skip scroll.
    if (diceActive) return;

    if (isFirstRender.current) {
      // Scroll directly on the container element — never scrollIntoView, which
      // bubbles up to body when the flex height chain loses min-h-0 constraints.
      container.scrollTop = container.scrollHeight;
      isFirstRender.current = false;
      return;
    }

    container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, [entries, preparing]);

  return (
    <div ref={containerRef} className="chat-log" aria-live="polite">
      {entries.map((entry, i) => {
        if (entry.kind === "player") {
          return (
            <div key={i}>
              {isGroupStart(entries, i) && (
                <div className="chat-attribution chat-attribution--player">Você</div>
              )}
              <p className="player-line">{entry.content}</p>
            </div>
          );
        }
        if (entry.kind === "roll") {
          return (
            <div key={i} className="roll-system-msg">
              <div className="text-wfrp-accent text-[10px] uppercase tracking-widest mb-1">
                Rolagem
              </div>
              {entry.content}
              {entry.success !== undefined && (
                <span className={`block mt-1 ${entry.success ? "text-green-400" : "text-red-400"}`}>
                  {entry.success ? "SUCESSO" : "FALHA"}
                </span>
              )}
            </div>
          );
        }
        if (entry.kind === "dice-roll") {
          // DiceOverlay covers the entire chat column while rolling — render nothing.
          return null;
        }
        if (entry.kind === "image") {
          return (
            <SceneImage
              key={entry.jobId}
              jobId={entry.jobId}
              imageType={entry.imageType}
              initialUrl={entry.url}
              initialStatus={entry.status}
              onReady={onImageReady}
            />
          );
        }
        if (entry.kind === "session-end") {
          return (
            <div
              key={i}
              className="max-w-prose my-8 mx-auto text-center border border-wfrp-border/60 rounded p-6 bg-wfrp-surface/60"
            >
              <div className="text-wfrp-muted text-[10px] uppercase tracking-[0.18em] mb-3 select-none">
                ✦
              </div>
              <p className="font-display text-base text-wfrp-muted mb-1">
                Sessão encerrada
              </p>
              {entry.xp > 0 && (
                <p className="text-wfrp-accent font-mono text-sm mb-5">
                  +{entry.xp} XP
                </p>
              )}
              <div className="flex gap-3 justify-center">
                <Link href="/campaigns" className="btn-primary text-sm px-4 py-2">
                  Continuar campanha
                </Link>
                <Link href="/session/end" className="btn-secondary text-sm px-4 py-2">
                  Encerrar por hoje
                </Link>
              </div>
            </div>
          );
        }
        return (
          <div key={i}>
            {isGroupStart(entries, i) && (
              <div className="chat-attribution">Mestre</div>
            )}
            <MarkdownNarrative
              content={entry.content}
              streaming={entry.streaming}
            />
          </div>
        );
      })}
      {preparing && (
        <p className="text-wfrp-muted text-sm animate-pulse select-none py-2">
          {t("session.preparingResponse")}
        </p>
      )}
      <div aria-hidden="true" />
    </div>
  );
}
