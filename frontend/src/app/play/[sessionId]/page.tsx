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
import { RequireAuth } from "@/contexts/AuthContext";
import { AudioMuteButton } from "@/components/audio/AudioMuteButton";
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
    awaitingFortuneDecision,
    diceRolling,
    showPrepare,
    diary,
    knownNpcs,
    rollHistory,
    sessionEnded,
    beginSession,
    sendAction,
    rollTest,
    beginFortuneReroll,
    continueAfterFailedRoll,
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
      <RequireAuth>
        <div className="game-shell items-center justify-center text-wfrp-muted">
          Carregando sessão…
        </div>
      </RequireAuth>
    );
  }

  const awaitingRoll = session.turn_phase === "awaiting_roll" && pendingTest;

  const currentDiceRoll = entries.find(
    (e): e is Extract<typeof entries[number], { kind: "dice-roll" }> => e.kind === "dice-roll"
  ) ?? null;

  return (
    <RequireAuth>
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
          <AudioMuteButton />
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
          {awaitingFortuneDecision && (
            <div className="px-5 pb-3">
              <div className="test-block">
                <p className="text-sm text-wfrp-muted mb-3">{t("session.fortuneRerollPrompt")}</p>
                <div className="flex flex-col sm:flex-row gap-2">
                  <button
                    type="button"
                    className="btn-primary flex-1"
                    disabled={loading || diceRolling}
                    onClick={beginFortuneReroll}
                  >
                    {t("session.fortuneReroll")}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary flex-1"
                    disabled={loading || diceRolling}
                    onClick={() => void continueAfterFailedRoll()}
                  >
                    {t("session.continueWithoutFortune")}
                  </button>
                </div>
              </div>
            </div>
          )}
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
                const textarea = e.currentTarget.elements.namedItem("action") as HTMLTextAreaElement;
                if (!textarea.value.trim() || awaitingRoll) return;
                const v = textarea.value.trim();
                textarea.value = "";
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
              <div className="flex gap-2 items-end">
                <textarea
                  name="action"
                  className="chat-input-textarea"
                  placeholder={t("session.placeholder")}
                  disabled={loading || !!awaitingRoll || diceRolling || sessionEnded}
                  autoComplete="off"
                  rows={1}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      e.currentTarget.form?.requestSubmit();
                    }
                  }}
                />
                <button
                  type="submit"
                  className="btn-primary px-3 shrink-0"
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
    </RequireAuth>
  );
}
