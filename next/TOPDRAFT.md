# Top-team draft and coordinated-objective development

The working bot is `ppo-topdraft-v3`, a separate fork of qualified v12. It uses
the rank-one draft and adds bounded, synchronized single-objective pushes.
It is a development candidate; platform v83 remains the deployed v12.
No PPO/BC model or critic was retrained, and no sealed confirmation cohort was used.

## Why this draft

[Intercontinental Fish](https://2026a.battlecode.co.uk/game/match-groups/005481ca-51a0-4e36-8542-cce33160738c)
picked Stellar, Heart of Ruin, Ren on three-pick maps, adding Cassi & Issac and
Ryth on five-pick maps. Its five games are all Patch 1.0.1. Our side was v81,
so those outcomes are excluded from PPO evaluation; their public opponent draft
is useful for scouting.

[Nyx](https://2026a.battlecode.co.uk/game/match-groups/d1a5ee25-5b2a-446c-bcda-ff889aacd32a)
picked Heart of Ruin, Ren, Ryth, adding Stellar and Tavi on five-pick maps.
Heart and Ren appear in 10/10 observed leader drafts; Stellar and Ryth in 8/10.
The [ladder](https://2026a.battlecode.co.uk/game/ladder) additionally shows ranks
one and two each using Heart, Ren and Stellar in their last 50 games; that
rolling window can include pre-hotfix games.

Use Fish's ordered priority, with all legal champions retained as fallbacks.
Four-pick maps use its four-pick prefix, an explicit extrapolation since no
four-pick leader game was in the sample. The original map classification remains
available to gameplay. The PPO adapter, 305 weights, purchases, fighting and
banking are unchanged in v1. Later versions change only objective coordination.

## Paired development evidence

Each version plays all 35 official maps in both seats against starter and its
stated reference, plus 100 generated screening maps in both seats against the
reference: 340 completed official release games per version, 1,020 overall.
All use CLI 3.0.2, engine 1.0.1. All 340 intended draft orders are checked per version.

| Version | Change | Starter wins | Reference wins | Reference | Faults | Fuel losses (all 340) |
|---|---|---:|---:|---|---:|---:|
| v1 | Fish draft only | 67/70 | 124/270 | qualified v12 | 0 | 42 |
| v2 | Periodic whole-team rally | 65/70 | 134/270 | draft-only v1 | 0 | 43 |
| v3 | One reachable staging point and latched assault | 67/70 | 136/270 | draft-only v1 | 0 | 33 |

These are development results, not a fresh promotion gate. Near-50% head-to-head
results do not establish a reliable general strength gain. Retain v1 as the draft
reference, reject v2's staging implementation, and keep v3 for further objective
and champion-specific work. It has not established an improvement over qualified
v12 and is not selected as the stable live bot. All three frozen source bundles
independently reproduce their WASM bytes; frozen versions remain immutable.

## Single-objective pushes

A public SDK probe of all 35 maps identifies exactly one gem-paying camp group
on `00stampede` (160 gems, 20 camp bodies) and `01elk-arena` (72 gems, eight bodies).
`01boss-battle` has 27 gem-paying groups, so this narrow rule does not apply there.
Other maps described as one farming area may need broader geometry detection.

From round 350, every 360 rounds provides a 240-round team campaign. Healthy,
empty-handed champions assemble at one reachable, home-side staging tile outside
camp attack range. A three-body team requires all three; a six-body Cassi/Issac
team requires five healthy bodies nearby. Once the quorum is seen, that champion
latches the assault for the current campaign, avoiding oscillation as front-line
allies move into camp range. Existing panic healing, banking, urgent self-defence,
shopping and movement-volley checks remain in place. The normal solo danger/claim
filter cannot silently discard the sole objective during the campaign. Between
campaigns the normal controller resumes. No new shared-memory bytes are used.

V2 staged around a large camp perimeter while counting readiness near its centre;
four full-log canaries recorded zero assault releases. V3 corrects that mismatch.
Four full-log canaries now record 96 per-champion assault releases, each with at
least five healthy bodies assembled; these are release events, not 96 distinct
whole-team attacks.

| Map | Our seat | v3 bank | v1 bank | v3 result |
|---|---|---:|---:|---|
| 00stampede | A | 160 | 640 | loss |
| 00stampede | B | 320 | 640 | loss |
| 01elk-arena | A | 288 | 72 | win |
| 01elk-arena | B | 648 | 72 | win |

The rally executes and improves elk-arena objective income, but Stampede still
regresses. Do not claim the single-objective weakness is solved generally.
Next isolate Heart's item build and farming/fight execution, then test objective
engagement timing and sustained damage on Stampede. Fish bought 498 Power Shards
of Focus on Heart across the five observed games; our Heart still inherits a
generic strength-oriented build. That is a concrete next hypothesis, not part of
this coordination experiment.

## Live learning loop

Fran authorized using every available hourly unranked challenge. The recorded
allowance was 24/50, and all 24 were used for 120 v83 games across the top ten
teams, all 35 maps, both seats. Each queued group recorded v83; all 120 official
summaries and replays were downloaded and independently reconstructed with the
official 1.0.1 WASM. Terminal outcome, round, deposits and per-champion kills,
deaths and gold match the official JSON exactly.

The batch wins 4/120, with zero bot faults, 29 fuel-exhausted turns (all on
01big-world), and 11 zero-bank games. PPO logs contain at least 10,276 calls and
5,428 target changes. This top-team batch is scouting, not an informative sole
progress benchmark. Initial Nyx 1/5 and automatic-ranked TTS 2/5 results remain
separate. The agent initiated only unranked games.

The active hourly automation now allocates approximately 60% near/moderately
stronger opponents, 30% stretch opponents and at most 10% leader scouting.
The initial nearby rank band is 0.7–1.1 times our current rank, adjusted using
actual results; rank percentages are not assumed to measure strength linearly.
Track banked gems, gold, deaths, objective captures and runtime alongside wins.
Keep a repeatable benchmark subset and pair the same map/opponent from both seats.
Fran permits automatic tested-bot uploads with brief notes such as `topdraft-v4`;
stable live selection still requires the applicable fresh promotion/runtime checks.

## Reproduction

The validation package contains frozen v1/v2/v3 sources, metadata and WASM, each
source ZIP, all 1,020 release match statistics/replays, public map-probe evidence,
four full-log canaries per rally attempt, and a SHA256 manifest. Restore `archive/`
into `next/`; use the included experiment `lab.toml` rather than changing the old
Stage 1–7 runtime pins. Initialize a separate official CLI 3.0.2 project, build
its starter-cpp, and run:

```sh
python tools/topdraft_screen.py --cli /path/to/cambc --runtime-project /path/to/current-project --config experiments/topdraft-v3/lab.toml --output /path/to/new-results
```

Official maps come from that current project, generated screening maps from
`next/maps/`. The old qualified v12 source, model and original certificates are
unchanged; this experiment does not relabel their 1.0.0 games as 1.0.1.
