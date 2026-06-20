"use client";

import { useCallback } from "react";
import { useParams } from "next/navigation";
import { CharacterSidebar } from "@/components/character/CharacterSidebar";
import { DiarySidebar } from "@/components/diary/DiarySidebar";
import { DiceOverlay } from "@/components/dice/DiceOverlay";
import { ResizeHandle, useSidebarWidths } from "@/components/layout/ResizeHandle";
import { ChatLog } from "@/components/session/ChatLog";
import { SessionPrepareOverlay } from "@/components/session/SessionPrepareOverlay";
import { TestBlock } from "@/components/session/TestBlock";
import { useSessionPlay } from "@/hooks/useSessionPlay";
import { t } from "@/lib/i18n";

export default function PlayPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const setSidebarWidths = useSidebarWidths(sessionId);

  const {
    session,
    character,
    entries,
    loading,
    pendingTest,
    diceRolling,
    showPrepare,
    diary,
    knownNpcs,
    rollHistory,
    sessionEnded,
    beginSession,
    sendAction,
    rollTest,
    handleDiceRollComplete,
    quickRoll,
    pauseSession,
    refreshCharacter,
  } = useSessionPlay(sessionId);

  const onResizeLeft = useCallback(
    (w: number) => {
      const right = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--right-w"), 10) || 260;
      setSidebarWidths(w, right);
    },
    [setSidebarWidths]
  );

  const onResizeRight = useCallback(
    (w: number) => {
      const left = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--left-w"), 10) || 280;
      setSidebarWidths(left, w);
    },
    [setSidebarWidths]
  );

  if (!session || !character) {
    return (
      <div className="game-shell items-center justify-center text-wfrp-muted">
        Carregando sessão…
      </div>
    );
  }

  const awaitingRoll = session.turn_phase === "awaiting_roll" && pendingTest;

  const currentDiceRoll = entries.find(
    (e): e is Extract<typeof entries[number], { kind: "dice-roll" }> => e.kind === "dice-roll"
  ) ?? null;

  return (
    <div className="game-shell">
      {showPrepare && (
        <SessionPrepareOverlay minutes={session.duration_minutes} onStart={beginSession} />
      )}

      <header className="game-header">
        <span className="font-display uppercase tracking-wider text-sm">
          {session.opening_location || session.tone || "Campanha"}
        </span>
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs text-wfrp-muted">
            {session.mode === "COMBATE"
              ? `${t("session.combat")} — turno ${session.combat_state?.turn ?? 1}`
              : t("session.minutesRemaining", { count: session.time_remaining_minutes })}
          </span>
          <button
            type="button"
            className="text-xs px-2 py-1 rounded border border-wfrp-border text-wfrp-muted hover:text-wfrp-fg hover:border-wfrp-accent/60 transition-colors disabled:opacity-40"
            disabled={loading || diceRolling}
            onClick={() => void pauseSession()}
            title="Pausar sessão e sair"
          >
            ⏸ Pausar
          </button>
        </div>
      </header>

      <div className="game-body">
        <aside className="sidebar-left">
          <CharacterSidebar
            character={character}
            sessionMode={session.mode}
            combatState={session.combat_state}
            timeRemaining={session.time_remaining_minutes}
            quickRollDisabled={!!awaitingRoll || loading || diceRolling}
            onQuickRoll={quickRoll}
          />
        </aside>

        <ResizeHandle side="left" onResize={onResizeLeft} />

        <section className="chat-column">
          <DiceOverlay
            visible={diceRolling}
            label={currentDiceRoll?.label}
            meta={currentDiceRoll?.meta}
            target={currentDiceRoll?.target}
            onDone={(roll) => {
              if (currentDiceRoll) void handleDiceRollComplete(currentDiceRoll.rollId, roll);
            }}
          />
          <ChatLog
            entries={entries}
            onImageReady={(job) => {
              if (job.image_type === "item" && job.status === "completed") {
                void refreshCharacter();
              }
            }}
          />
          {awaitingRoll && (
            <div className="px-5">
              <TestBlock pending={pendingTest} onRoll={rollTest} disabled={loading || diceRolling} />
            </div>
          )}
          {loading && !diceRolling && (
            <p className="px-5 text-wfrp-muted text-sm animate-pulse">{t("session.gmNarrates")}</p>
          )}

          <div className="chat-input-area">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const input = (e.currentTarget.elements.namedItem("action") as HTMLInputElement);
                if (!input.value.trim() || awaitingRoll) return;
                const v = input.value.trim();
                input.value = "";
                void sendAction(v);
              }}
            >
              <p className="text-xs text-wfrp-muted mb-2">
                {sessionEnded
                  ? t("session.ended")
                  : awaitingRoll
                    ? t("session.pendingTest")
                    : t("session.pauseHint")}
              </p>
              <div className="flex gap-2">
                <input
                  name="action"
                  className="flex-1 bg-wfrp-surface border border-wfrp-border rounded px-3 py-2 text-wfrp-fg"
                  placeholder={t("session.placeholder")}
                  disabled={loading || !!awaitingRoll || diceRolling || sessionEnded}
                  autoComplete="off"
                />
                <button
                  type="submit"
                  className="btn-primary px-3"
                  disabled={loading || !!awaitingRoll || diceRolling || sessionEnded}
                  aria-label="Enviar"
                >
                  →
                </button>
              </div>
            </form>
          </div>
        </section>

        <ResizeHandle side="right" onResize={onResizeRight} />

        <aside className="sidebar-right">
          <DiarySidebar campaignEntries={diary} knownNpcs={knownNpcs} rollHistory={rollHistory} />
        </aside>
      </div>
    </div>
  );
}
