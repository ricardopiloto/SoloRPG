import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { DiceRoller, type RollResult } from "@/components/DiceRoller";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Tavern of Rolls — RPG Dice Table" },
      {
        name: "description",
        content:
          "A live RPG table with a 3D dice roller, character sheet, party panel, and campaign log.",
      },
    ],
  }),
  component: GameTable,
});

const CHARACTER = {
  name: "Kaelen Vorr",
  title: "Half-Elf Warlock of the Hollow Pact",
  level: 5,
  hp: { now: 32, max: 38 },
  ac: 14,
  init: "+3",
  prof: "+3",
  speed: "30 ft",
  stats: [
    { k: "STR", v: 9, m: "-1" },
    { k: "DEX", v: 16, m: "+3" },
    { k: "CON", v: 14, m: "+2" },
    { k: "INT", v: 12, m: "+1" },
    { k: "WIS", v: 11, m: "+0" },
    { k: "CHA", v: 18, m: "+4" },
  ],
  skills: [
    { k: "Arcana", v: "+4" },
    { k: "Deception", v: "+7" },
    { k: "Persuasion", v: "+7" },
    { k: "Perception", v: "+3" },
  ],
  spells: [
    "Eldritch Blast (1d10 force)",
    "Hex (1d6 necrotic)",
    "Misty Step",
    "Hold Person",
    "Counterspell",
  ],
};

const PARTY = [
  { name: "Brina Stoneward", role: "Dwarf Cleric", hp: "41/41", color: "var(--color-gold)" },
  { name: "Sable", role: "Tabaxi Rogue", hp: "27/30", color: "oklch(0.7 0.18 160)" },
  { name: "Orso the Ember", role: "Goliath Barbarian", hp: "18/52", color: "oklch(0.6 0.22 30)" },
];

const SCENE = {
  campaign: "The Whispering Crown",
  session: "Session XII · The Drowned Vault",
  location: "Beneath Cael Morath — Tide Cathedral",
  weather: "Pitch dark · brackish water · echoes of distant chanting",
  objective:
    "Recover the Lantern of Hours before the moon completes its passage over the inverted altar.",
};

function GameTable() {
  const [log, setLog] = useState<RollResult[]>([]);

  return (
    <div className="min-h-screen w-full">
      {/* Top bar */}
      <header className="flex items-center justify-between border-b border-[color:var(--color-border)] px-6 py-3">
        <div className="flex items-center gap-3">
          <div
            aria-hidden
            className="grid h-9 w-9 place-items-center rounded-md border border-[color:var(--color-gold)]/40"
            style={{ background: "linear-gradient(180deg,var(--blood),oklch(0.22 0.04 30))" }}
          >
            <span style={{ color: "var(--color-gold)", fontFamily: "var(--font-display)" }}>
              20
            </span>
          </div>
          <div>
            <h1 className="text-lg leading-none" style={{ color: "var(--color-gold)" }}>
              Tavern of Rolls
            </h1>
            <p className="text-xs text-[color:var(--color-muted-foreground)]">
              {SCENE.campaign} · {SCENE.session}
            </p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-6 text-xs">
          <span className="stat-label">Round 3</span>
          <span className="stat-label">Turn — Kaelen</span>
          <span
            className="rounded-full border border-[color:var(--color-gold)]/40 px-3 py-1"
            style={{ color: "var(--color-gold)", fontFamily: "var(--font-display)" }}
          >
            Initiative
          </span>
        </div>
      </header>

      {/* Main 3-column layout */}
      <main className="grid gap-4 p-4 lg:grid-cols-[320px_1fr_320px] lg:p-6 lg:h-[calc(100vh-64px)]">
        {/* LEFT — Character */}
        <aside className="panel flex flex-col gap-4 overflow-y-auto p-5">
          <div>
            <p className="panel-heading">Character</p>
            <h2 className="mt-1 text-2xl leading-tight" style={{ color: "var(--color-parchment)" }}>
              {CHARACTER.name}
            </h2>
            <p className="text-sm italic text-[color:var(--color-muted-foreground)]">
              {CHARACTER.title}
            </p>
          </div>

          <div className="ornament-divider" />

          <div className="grid grid-cols-3 gap-2 text-center">
            <Mini label="LVL" value={CHARACTER.level} />
            <Mini label="AC" value={CHARACTER.ac} />
            <Mini label="INIT" value={CHARACTER.init} />
          </div>

          <div>
            <div className="flex items-baseline justify-between">
              <span className="stat-label">Hit Points</span>
              <span className="stat-value">
                {CHARACTER.hp.now}/{CHARACTER.hp.max}
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-[color:var(--color-input)]">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${(CHARACTER.hp.now / CHARACTER.hp.max) * 100}%`,
                  background:
                    "linear-gradient(90deg, oklch(0.55 0.2 25), oklch(0.78 0.15 60))",
                }}
              />
            </div>
          </div>

          <div>
            <p className="panel-heading mb-2">Ability Scores</p>
            <div className="grid grid-cols-3 gap-2">
              {CHARACTER.stats.map((s) => (
                <div
                  key={s.k}
                  className="rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-input)]/40 p-2 text-center"
                >
                  <div className="stat-label">{s.k}</div>
                  <div
                    className="text-xl"
                    style={{ color: "var(--color-gold)", fontFamily: "var(--font-display)" }}
                  >
                    {s.v}
                  </div>
                  <div className="text-xs text-[color:var(--color-muted-foreground)]">{s.m}</div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="panel-heading mb-2">Skills</p>
            {CHARACTER.skills.map((s) => (
              <div key={s.k} className="stat-row">
                <span className="text-sm">{s.k}</span>
                <span className="stat-value text-sm">{s.v}</span>
              </div>
            ))}
          </div>

          <div>
            <p className="panel-heading mb-2">Known Spells</p>
            <ul className="space-y-1 text-sm">
              {CHARACTER.spells.map((sp) => (
                <li
                  key={sp}
                  className="flex items-start gap-2 text-[color:var(--color-foreground)]/90"
                >
                  <span style={{ color: "var(--color-gold)" }}>✦</span> {sp}
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* CENTER — Dice */}
        <section className="flex min-h-[60vh] flex-col">
          <DiceRoller onRoll={(r) => setLog((l) => [r, ...l].slice(0, 20))} />
        </section>

        {/* RIGHT — Game info */}
        <aside className="panel flex flex-col gap-4 overflow-y-auto p-5">
          <div>
            <p className="panel-heading">Current Scene</p>
            <h2
              className="mt-1 text-xl leading-tight"
              style={{ color: "var(--color-parchment)" }}
            >
              {SCENE.location}
            </h2>
            <p className="mt-1 text-sm italic text-[color:var(--color-muted-foreground)]">
              {SCENE.weather}
            </p>
          </div>

          <div className="ornament-divider" />

          <div>
            <p className="panel-heading mb-1">Objective</p>
            <p className="text-sm leading-relaxed">{SCENE.objective}</p>
          </div>

          <div>
            <p className="panel-heading mb-2">The Party</p>
            <ul className="space-y-2">
              {PARTY.map((p) => (
                <li
                  key={p.name}
                  className="flex items-center gap-3 rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-input)]/40 p-2"
                >
                  <span
                    className="grid h-8 w-8 place-items-center rounded-full text-xs font-semibold"
                    style={{ background: p.color, color: "oklch(0.15 0.02 40)" }}
                  >
                    {p.name
                      .split(" ")
                      .map((n) => n[0])
                      .slice(0, 2)
                      .join("")}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="truncate text-sm" style={{ color: "var(--color-parchment)" }}>
                      {p.name}
                    </div>
                    <div className="text-xs text-[color:var(--color-muted-foreground)]">
                      {p.role}
                    </div>
                  </div>
                  <span className="stat-value text-sm">{p.hp}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="ornament-divider" />

          <div className="flex-1 min-h-0 flex flex-col">
            <p className="panel-heading mb-2">Roll Log</p>
            <div className="flex-1 overflow-y-auto pr-1">
              {log.length === 0 ? (
                <p className="text-sm italic text-[color:var(--color-muted-foreground)]">
                  No rolls yet. Take aim at fate.
                </p>
              ) : (
                <ul className="space-y-1.5">
                  {log.map((r) => (
                    <li
                      key={r.id}
                      className="flex items-center justify-between rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-input)]/30 px-3 py-2 text-sm"
                    >
                      <div>
                        <div style={{ color: "var(--color-parchment)" }}>{r.notation}</div>
                        <div className="text-xs text-[color:var(--color-muted-foreground)]">
                          {r.values.join(" · ")}
                        </div>
                      </div>
                      <span
                        className="text-2xl"
                        style={{
                          color: "var(--color-gold)",
                          fontFamily: "var(--font-display)",
                        }}
                      >
                        {r.total}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}

function Mini({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-[color:var(--color-border)] bg-[color:var(--color-input)]/40 p-2">
      <div className="stat-label">{label}</div>
      <div
        className="text-xl"
        style={{ color: "var(--color-gold)", fontFamily: "var(--font-display)" }}
      >
        {value}
      </div>
    </div>
  );
}
