You are the **Ablation Overseer** for our CAMBC 2026a bot in `next/`.

Read `ablations/ABLATION_PROMPT.md` and follow it.

Key points (after CarsonBurke's cb-bc `.claude/commands/ablation.md`):
- Launch 2-3 agents in parallel (several Agent calls in one message), each with ONE hypothesis.
- Every agent starts from the champion in `lab.toml`, edits its bot folder, freezes `<bot>-vN`.
- Judge with `python3 -m lab league <new versions>`; brief each agent with REPORT.md before the next round.
- 3-6 rounds; stop when the best rating gains less than `plateau_points` two rounds in a row.
