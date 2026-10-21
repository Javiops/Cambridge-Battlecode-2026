# Optional spell-scan guard: v9 rejected

V9 changes only `spell_sweep`'s entry guard from 22,000 to 41,000 remaining
fuel (the helper adds the existing 16,000 reserve). Initialization's global
reserve is unchanged. This tests a plausible optional-work boundary, not an
established attribution to a specific native call.

Ten full-log release canaries cover big-world and ambush against starter/v8,
both seats, plus both seats of generated g1-screen-093 against v8. All finish
with zero faults. The target B-seat failure still has **94 exhausted turns**;
there is one ambush exhausted turn against each opponent. Reject this change
because it does not solve the named failure. No broad screen, promotion or
upload follows a failed targeted hypothesis. V9 is frozen and independently
rebuilt exactly; working source returns to frozen v8 without mutating v9.

The known performance concern is matchup-dependent, and was already present
in v7: B has 94 losses with either v7 or v8 in their reverse-seat pair. Against
fixed v6 both versions have zero on this layout and 14 across the full broad
schedule. Preserve that distinction. Heavy printf instrumentation substantially
changes fuel behavior; a lighter diagnostic also changes the trajectory. Neither
identifies the culprit conclusively. Next use a cheaper targeted native-call
diagnostic or isolate a bounded optional operation with new evidence.

See `results/topdraft-v9-canary.json` and its per-game JSONL. V8 remains the
prepared experiment. The teammate live hold remains active, with v82 selected
and no v85 unranked requests initiated by this agent.
