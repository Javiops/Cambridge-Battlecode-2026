# Far pieces on the fuel-free base b32 (far-maps thread, 10-25 ~10:55 UTC)

- **Base:** fuelfit-b32 (branch claude/project-thread-jeb4pf, sha 76d0a735).
- **Pieces:** opts/o80_fargw.py and opts/o81_farout.py. Same format as handoff/fuelfit/opts: each takes SRCDIR, uses exact replacements and asserts if they do not match.
- **Rules followed:** no fuel reads, no printf, no work at start-up. Both act only from r400, on maps with g_tpc_path >= 60 (draft memory byte 29, already read by init).
- **Check:** applying the opts to b32/src gives byte-identical replays to my local builds (islands, expanse).

## What each piece does
- **o80 fargw:** gold weight 0.33 in choose_target in r400-800 on far maps.
  - Why: far is a gem race decided in r400-800.
- **o81 farout:** from r400 on far maps, when outnumbered by 2+ within 8, recall if it cannot be interrupted, otherwise back off.
  - Why: online, being outnumbered at a contact killed us 21% of the time and the rival 0%.

## Local far bench (84 games: 14 far maps x pHuntF/rRushHunt/rTop1 x 2 sides), against b32
b32 alone wins 74/84.

| Candidate | Changed games | First gem divergence | Wins | Net | r800 gem margin |
|---|---|---|---|---|---|
| b32+o80 | 83/84 | r440 (median r526) | 76 | +7 −5 = +2 | +21.0 (se 11.0) |
| b32+o81 | 31/84 | r439 (median r817) | 72 | +1 −3 = −2 | +2.0 (se 2.5) |
| b32+o80+o81 | 83/84 | r439 (median r517) | 77 | +7 −4 = +3 | +23.4 (se 11.8) |

With determinism, nothing changes before r400 in any game. Each piece only moves the games where it acts.

## Ask
J2 on the PC against b32 for:
1. b32 + o80.
2. b32 + o80 + o81.

Report far, mid and near separately. Mid and near should be 0, because both pieces only act on far maps.

**Status (10:30 UTC):** PARKED. These pieces are not sent to the PC. The user paused late pieces (r400+) on 10-24 at 08:41, and these diverge at r440. They are kept here in case the user reopens the late game.

## o82 farnochase (10-25, early piece, on b35)
- Mechanism: online V20 far r150-400 we walk 126 rounds/team that end in a champion fight vs rival 81, same fight rounds; we chase from further. Local b35 vs rTop1 does not reproduce it (92 vs 101).
- Rule: far (g_tpc_path >= 60), round < 400 (P_FNC_R1): team-fight chase layer (P_CHASE/P_TF_GUARD) off. No fuel read, no printf.
- Local far bench vs b35 (84 g): changes 42/84, divergence median r263 (min r116); wins net -1; col400 us -0.9 them -3.6; r800 margin +5.4 (se 10.9), deaths -0.23. Neutral locally as expected; only PC/online can judge.
- Zip: bot/far-b32/b35-fnc.zip (b35 4ecb5c9 + opts/o82_farnochase.py).
