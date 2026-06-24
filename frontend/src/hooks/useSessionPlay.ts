"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  api,
  CampaignNpc,
  Character,
  PendingTest,
  RollHistoryEntry,
  SessionDetail,
  SessionTurnOut,
  TurnResponse,
} from "@/lib/api";
import type { ChatEntry } from "@/components/session/ChatLog";
import type { QuickRollTarget } from "@/components/character/QuickRollPopover";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

function turnsToEntries(turns: SessionTurnOut[]): ChatEntry[] {
  return turns.flatMap((t): ChatEntry[] => {
    if (t.role === "player") {
      return [{ kind: "player", content: t.content }];
    }
    if (t.role === "gm") {
      return [{ kind: "narrative", content: t.content }];
    }
    if (t.role === "system") {
      const meta = t.metadata as Record<string, unknown> | null | undefined;
      const qr = meta?.quick_roll as Record<string, unknown> | undefined;
      if (qr) {
        return [
          {
            kind: "roll",
            content: (qr.llm_text as string) || t.content,
            success: qr.success as boolean | undefined,
          },
        ];
      }
    }
    return [];
  });
}

export function useSessionPlay(sessionId: string) {
  const router = useRouter();
  const { setMood } = useAudioPlayer();
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [character, setCharacter] = useState<Character | null>(null);
  const [entries, setEntries] = useState<ChatEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [pendingTest, setPendingTest] = useState<PendingTest | null>(null);
  const pendingRollCtxRef = useRef<
    | { type: "test"; rollId: string }
    | { type: "fortune-reroll"; rollId: string }
    | { type: "quick"; target: QuickRollTarget; modifier: number; rollId: string }
    | null
  >(null);
  const [awaitingFortuneDecision, setAwaitingFortuneDecision] = useState(false);
  const [showPrepare, setShowPrepare] = useState(true);
  const [diary, setDiary] = useState<Array<{ content: string }>>([]);
  const [knownNpcs, setKnownNpcs] = useState<CampaignNpc[]>([]);
  const [started, setStarted] = useState(false);
  const [rollHistory, setRollHistory] = useState<RollHistoryEntry[]>([]);
  const historyLoadedRef = useRef(false);

  const load = useCallback(async () => {
    const s = await api.getSession(sessionId);

    // If paused, auto-resume on page entry
    if (s.paused_at) {
      const resumed = await api.resumeSession(sessionId);
      setSession(resumed);
    } else {
      setSession(s);
    }

    if (s.character_id) {
      setCharacter(await api.getCharacter(s.character_id));
    }
    const [diaryData, npcData] = await Promise.all([
      api.getDiary(s.campaign_id),
      api.listCampaignNpcs(s.campaign_id),
    ]);
    setDiary(diaryData.map((d) => ({ content: d.content })));
    setKnownNpcs(npcData.npcs);

    // Restore history from server (source of truth), avoiding duplicate loads
    if (!historyLoadedRef.current) {
      historyLoadedRef.current = true;
      const turns = await api.getSessionHistory(sessionId);
      if (turns.length > 0) {
        setEntries(turnsToEntries(turns));
        setStarted(true);
        setShowPrepare(false);
      } else {
        // No turns — check sessionStorage as fallback for in-memory state
        const prepared = sessionStorage.getItem(`wfrp-prepared-${sessionId}`);
        if (prepared === "1") setShowPrepare(false);
        const wasStarted = sessionStorage.getItem(`wfrp-started-${sessionId}`);
        if (wasStarted === "1") setStarted(true);
      }
    }
  }, [sessionId]);

  useEffect(() => {
    load().catch(console.error);
  }, [load]);

  const appendImages = useCallback((images: TurnResponse["images"]) => {
    if (!images?.length) return;
    setEntries((prev) => {
      const existing = new Set(prev.filter((e) => e.kind === "image").map((e) => e.jobId));
      const next = images
        .filter((img) => !existing.has(img.job_id) && img.status !== "failed")
        .map((img) => ({
          kind: "image" as const,
          jobId: img.job_id,
          imageType: img.type,
          url: img.url,
          status: img.status ?? "pending",
        }));
      return next.length ? [...prev, ...next] : prev;
    });
  }, []);

  const appendRolls = useCallback((rolls: TurnResponse["roll_results"], spontaneous = false) => {
    if (!rolls?.length) return;
    const rollEntries: RollHistoryEntry[] = rolls
      .filter((r) => r.roll !== undefined && r.target !== undefined)
      .map((r) => ({
        label: r.skill || r.attribute || r.type || "Rolagem",
        roll: r.roll!,
        target: r.target!,
        success: r.success ?? false,
        levels: Math.abs(Math.floor((r.target! - r.roll!) / 10)),
        type: r.type,
        spontaneous,
        timestamp: Date.now(),
      }));
    if (rollEntries.length) {
      setRollHistory((prev) => [...prev, ...rollEntries]);
    }
  }, []);

  const applyMeta = useCallback(
    async (result: TurnResponse) => {
      if (result.scene_mood) {
        setMood(result.scene_mood);
      }
      appendImages(result.images);
      appendRolls(result.roll_results);
      if (session) {
        setSession({
          ...session,
          time_remaining_minutes: result.time_remaining_minutes,
          mode: result.mode,
          turn_phase: result.turn_phase,
          combat_state: result.combat_state ?? session.combat_state,
        });
      }
      if (result.turn_phase === "awaiting_roll" && result.pending_test) {
        setPendingTest(result.pending_test);
      } else if (result.turn_phase === "normal") {
        setPendingTest(null);
      }
      if (result.session_ended) {
        sessionStorage.setItem(
          "wfrp-recap",
          JSON.stringify({
            summary: result.player_summary || result.narrative,
            xp: result.xp_awarded,
            campaignId: session?.campaign_id,
            characterId: session?.character_id,
          })
        );
        setEntries((prev) => [
          ...prev,
          {
            kind: "session-end" as const,
            xp: result.xp_awarded,
            playerSummary: result.player_summary,
            campaignId: session?.campaign_id,
            characterId: session?.character_id,
          },
        ]);
      }
      if (session?.campaign_id) {
        const [diaryData, npcData] = await Promise.all([
          api.getDiary(session.campaign_id),
          api.listCampaignNpcs(session.campaign_id),
        ]);
        setDiary(diaryData.map((d) => ({ content: d.content })));
        setKnownNpcs(npcData.npcs);
      }
      if (character?.id && result.roll_results.some((r) => "wounds_applied" in r && r.wounds_applied)) {
        setCharacter(await api.getCharacter(character.id));
      }
    },
    [session, character, router, appendImages, appendRolls, setMood]
  );

  const runStreamTurn = useCallback(
    async (action: string) => {
      let streamed = "";
      let finalResult: TurnResponse | null = null;
      for await (const event of api.streamAction(sessionId, action)) {
        if (event.type === "token") {
          streamed += event.content;
          setEntries((prev) => {
            const last = prev[prev.length - 1];
            if (last?.kind === "narrative" && last.streaming) {
              return [...prev.slice(0, -1), { kind: "narrative", content: streamed, streaming: true }];
            }
            return [...prev, { kind: "narrative", content: streamed, streaming: true }];
          });
        } else if (event.type === "done") {
          finalResult = event;
        }
      }
      if (finalResult) {
        setEntries((prev) => {
          const trimmed = prev.filter((e) => !(e.kind === "narrative" && e.streaming));
          if (finalResult!.narrative) {
            return [...trimmed, { kind: "narrative", content: finalResult!.narrative }];
          }
          return trimmed;
        });
        await applyMeta(finalResult);
      }
    },
    [sessionId, applyMeta]
  );

  const beginSession = useCallback(async () => {
    sessionStorage.setItem(`wfrp-prepared-${sessionId}`, "1");
    setShowPrepare(false);
    if (!started) {
      sessionStorage.setItem(`wfrp-started-${sessionId}`, "1");
      setStarted(true);
      setLoading(true);
      try {
        await runStreamTurn("Início da sessão.");
      } finally {
        setLoading(false);
      }
    }
  }, [sessionId, started, runStreamTurn]);

  const sendAction = useCallback(
    async (action: string) => {
      setEntries((prev) => [...prev, { kind: "player", content: action }]);
      setLoading(true);
      try {
        await runStreamTurn(action);
      } finally {
        setLoading(false);
      }
    },
    [runStreamTurn]
  );

  const streamRollNarrate = useCallback(async () => {
    let streamed = "";
    let finalResult: TurnResponse | null = null;
    for await (const event of api.streamRollNarrate(sessionId)) {
      if (event.type === "token") {
        streamed += event.content;
        setEntries((prev) => {
          const last = prev[prev.length - 1];
          if (last?.kind === "narrative" && last.streaming) {
            return [
              ...prev.slice(0, -1),
              { kind: "narrative", content: streamed, streaming: true },
            ];
          }
          return [...prev, { kind: "narrative", content: streamed, streaming: true }];
        });
      } else if (event.type === "done") {
        finalResult = event;
      }
    }
    if (finalResult) {
      setEntries((prev) => {
        const trimmed = prev.filter((e) => !(e.kind === "narrative" && e.streaming));
        return [...trimmed, { kind: "narrative", content: finalResult!.narrative }];
      });
      await applyMeta(finalResult);
    }
  }, [sessionId, applyMeta]);

  const applyRollResponse = useCallback(
    (res: import("@/lib/api").RollResultResponse) => {
      appendRolls(res.roll_results);
      if (session) {
        setSession({
          ...session,
          turn_phase: res.turn_phase,
          mode: res.mode,
          combat_state: res.combat_state ?? session.combat_state,
        });
      }
      if (character && res.fortune_current != null && res.fortune_max != null) {
        setCharacter({
          ...character,
          fortune_current: res.fortune_current,
          fortune_max: res.fortune_max,
        });
      }
      return res.roll_results.some((r) => r.success === false);
    },
    [session, character, appendRolls]
  );

  const continueAfterFailedRoll = useCallback(async () => {
    setAwaitingFortuneDecision(false);
    setLoading(true);
    try {
      await streamRollNarrate();
    } finally {
      setLoading(false);
    }
  }, [streamRollNarrate]);

  const beginFortuneReroll = useCallback(() => {
    const rollId = crypto.randomUUID();
    pendingRollCtxRef.current = { type: "fortune-reroll", rollId };
    setAwaitingFortuneDecision(false);
    setEntries((prev) => [
      ...prev,
      {
        kind: "dice-roll" as const,
        rollId,
        label: "Re-roll com Fortuna",
        meta: "d100",
      },
    ]);
  }, []);

  const rollTest = useCallback(() => {
    if (!pendingTest) return;
    const rollId = crypto.randomUUID();
    pendingRollCtxRef.current = { type: "test", rollId };
    const p = pendingTest.payload;
    const label = p.pericia || p.descricao || p.atributo || "Teste";
    const metaParts: string[] = [];
    if (p.atributo) metaParts.push(p.atributo);
    if (p.modificador != null && p.modificador !== 0) {
      metaParts.push(`Mod ${p.modificador > 0 ? "+" : ""}${p.modificador}`);
    }
    if (p.descricao) metaParts.push(p.descricao);
    const meta = metaParts.length ? metaParts.join(" · ") : "d100";
    setEntries((prev) => [
      ...prev,
      { kind: "dice-roll" as const, rollId, label, meta },
    ]);
  }, [pendingTest]);

  const handleDiceRollComplete = useCallback(
    async (rollId: string, animationRoll: number) => {
      setEntries((prev) =>
        prev.filter((e) => !(e.kind === "dice-roll" && e.rollId === rollId))
      );

      const ctx = pendingRollCtxRef.current;
      if (!ctx || ctx.rollId !== rollId) return;
      pendingRollCtxRef.current = null;

      setLoading(true);
      try {
        if (ctx.type === "test") {
          const res = await api.rollTest(sessionId, animationRoll);
          applyRollResponse(res);
          if (res.fortune_reroll_available) {
            setAwaitingFortuneDecision(true);
            return;
          }
          await streamRollNarrate();
        } else if (ctx.type === "fortune-reroll") {
          const res = await api.fortuneReroll(sessionId, animationRoll);
          applyRollResponse(res);
          if (res.fortune_reroll_available) {
            setAwaitingFortuneDecision(true);
            return;
          }
          await streamRollNarrate();
        } else if (ctx.type === "quick") {
          const res = await api.quickRoll(
            sessionId,
            ctx.target.type,
            ctx.target.key,
            ctx.modifier,
            animationRoll
          );
          setEntries((prev) => [
            ...prev,
            { kind: "roll", content: res.narration_hint, success: res.success },
          ]);
          setRollHistory((prev) => [
            ...prev,
            {
              label: res.key,
              roll: res.roll,
              target: res.target,
              success: res.success,
              levels: Math.abs(res.levels),
              type: res.roll_type,
              spontaneous: true,
              timestamp: Date.now(),
            },
          ]);
        }
      } finally {
        setLoading(false);
      }
    },
    [sessionId, session, character, applyRollResponse, streamRollNarrate]
  );

  const quickRoll = useCallback((target: QuickRollTarget, modifier: number): Promise<void> => {
    const rollId = crypto.randomUUID();
    pendingRollCtxRef.current = { type: "quick", target, modifier, rollId };
    const effectiveTarget = Math.max(1, Math.min(100, target.target + modifier));
    const meta =
      `Alvo ${effectiveTarget}` +
      (modifier !== 0 ? ` · Mod ${modifier > 0 ? "+" : ""}${modifier}` : "");
    setEntries((prev) => [
      ...prev,
      {
        kind: "dice-roll" as const,
        rollId,
        label: target.label,
        meta,
        target: effectiveTarget,
      },
    ]);
    return Promise.resolve();
  }, []);

  const diceRolling = entries.some((e) => e.kind === "dice-roll");

  const pauseSession = useCallback(async () => {
    try {
      await api.pauseSession(sessionId);
      router.push("/campaigns");
    } catch (e) {
      console.error("Falha ao pausar sessão:", e);
    }
  }, [sessionId, router]);

  const refreshCharacter = useCallback(async () => {
    if (!session?.character_id) return;
    setCharacter(await api.getCharacter(session.character_id));
  }, [session?.character_id]);

  const sessionEnded = entries.some((e) => e.kind === "session-end");

  return {
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
  };
}
