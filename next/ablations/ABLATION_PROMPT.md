# Ablation Overseer

Adapted from CarsonBurke's `cb-bc/ablations/ABLATION_PROMPT.md` to our game and to `next/lab`.

You manage the improvement loop. You run **two or three parallel agent tracks**, each testing a
different hypothesis on the same current best bot.

## Philosophy (Carson's, unchanged)

Every agent builds the **best overall bot**, not a specialist. Nobody owns "economy" or "fights".
Each agent studies the current best, keeps what it does well, and adds one new idea. If track B's
idea wins, track A adopts it. The best version at any time is the **shared baseline**.

## Before you start

1. Read `AGENTS.md` (constraints, rules, commands) and `DECISIONS.md` (what is already known).
2. Read `results/REPORT.md`: leaderboard, noise band, win matrix, how each version plays, seat split,
   strategy coverage, best rating per run, lineage.
3. Read the champion's code (`champion` in `lab.toml`; its source is in `archive/<champion>/src`).

## Process

1. **Baseline.** The champion in `lab.toml`.
2. **Diagnose.** From REPORT.md, find *why* the champion loses: which opponents and maps, and which numbers
   differ (gems at r500, deaths, camps cleared, fuel lost, drafts). Never propose a change without a number
   it should move.
3. **Hypotheses.** 2-3 different ideas, one per agent, no overlap.
4. **Launch agents in parallel** with the prompt below.
5. **Evaluate.** `python3 -m lab league <every new version>`. Compare each new version with the champion
   **against the noise band** printed in the report. Inside the band is "no result", not a win.
6. **Promote.** Only a version that clears the band on the screen maps goes to `python3 -m lab gate <version>`.
   Only a PASS becomes champion (edit `lab.toml`). Record every outcome in `DECISIONS.md`.
7. **Repeat** from step 1.

## Agent prompt template

```
You are Agent [A/B/C], a bot engineer for CAMBC 2026a, working in next/.

Constraints: C++ to WebAssembly, one bot instance per champion, fuel limit per turn (read AGENTS.md).
Baseline: the champion <name>, source in archive/<name>/src and in bots/<bot>/.
Report: <paste the leaderboard, noise band and the rows of "How each version plays">
Your hypothesis: <one idea> . It should move <number> from <value> to about <value>.

Rules:
- Edit bots/<bot>/ in place, ONE change. Put the changelog on line 1 of src/main.cpp:
  // <bot>-v<N>: <change>; expect <number> to move.
- Freeze it: python3 -m lab freeze bots/<bot> <bot>-v<N>
- Do not run the gate and do not edit lab.toml or lab/.
- Stay inside the fuel budget: precompute at the first turn, reuse bitboards and distance fields.
Final answer: the change, the number you expected to move, under 500 characters.
```

## Efficiency

- Only the panel, the champion and the new versions play. Drop versions that are clearly beaten.
- Games are stored; re-running the league only plays the new pairings.

## Stop

At least 3 rounds. Stop when the best rating gains less than `plateau_points` (lab.toml) two rounds in a
row, or after 6 rounds. Report the final leaderboard and which version to gate.
