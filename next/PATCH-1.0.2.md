# Patch 1.0.2 verified

The active development runtime is official **CLI 3.0.4 / engine 1.0.2**, build
ff41468c05c7be716f7647aaf7ea7314633f7038815386c806fafcec98629114.
The signed-in download page checksum matches the downloaded executable. The
official engine and new replay version are131073; new captures use a separately
pinned native decoder. Historical 1.0.1 runs and Stage 1–7 certificates remain intact.

The official 21 October patch reduces Stellar health 750→650,health/shard 75→65,
focus 85→70 and focus/shard 9→7;Heart strength 40→30,strength/shard 4→3.5 and dash
damage 1.75→1.5focus;Ren stun damage 1.25→0.75focus. It buffs Vesper health 900→1000
and strength 50→55,Vendetta health 800→1000,Tavi health 750→900 and focus 100→110,
and Prism passive focus/gem 1→1.5. Source:
https://2026a.battlecode.co.uk/game/patch-notes/e251fa42-fb2a-4d9b-ab8c-2e044f21d599

## Unchanged bot under the new rules

Two independent extractions of v19's frozen source ZIP compile with the updated
SDK to the **identical** original release WASM 301031fc5a4d34b5ddd263605485a349007e54e7ac8817e0a342307c9457851b.
The source,draft,model and parameters were not changed. Live platform 93 is freshly
verified;new server games actually report 1.0.2/build ff41468c. No re-upload is needed
and no server binary hash is claimed. All 35 official map files remain byte-identical.

Across 35 official + 140 generated development maps,both seats,the unchanged candidate
wins 69/70 against starter and 172/350 against parent v18,zero faults,**10 exhausted turns**. Twenty-six
additional full-log canaries exactly repeat outcomes,rounds,picks,team and own
champion statistics:12/12 against starter, 6/14 against parent,zero faults,two repeated fuel turns.
There are 446 new runs covering 420 unique fixtures;do not double-count repeated fuel.
Big-world starter deposits 885/815,with one B-seat exhausted turn.

All 420 seeds and candidate,parent and starter WASM identities match the historical
1.0.1 comparison. Old results were 69/70 against starter, 173/350 against parent and 4 fuel turns;
275/420 outcomes match under the new rules. This measures patch sensitivity,not a
source improvement or calibrated strength gain. The lab champion and 70 unused
confirmation maps are unchanged. Occasional exhaustion remains a limitation;
there is no persistent fault or stalled-play evidence requiring rollback.

## New unranked cohort: collection continues

All 50 available challenges were used:250 new games, 35 maps,both seats,
30 nearby / 16 stretch / 4 leader groups,all queued version 93. No unknown/pending request
or duplicate. Actual request-end allowance 0. This is a new fixture window,
separate from the completed 250-game 1.0.1 benchmark.

At this checkpoint, 10 groups / 50 games are collected and native-verified:
21 wins,zero faults,one exhausted turn. These first 50 are Plantir only;do not
generalize them to the full curriculum.40 groups remain to collect. Read CURRENT.json
and the active journal for later progress. Unranked games do not change Elo;
incoming and automatic ranked games are excluded from our initiated tests.

Next finish collection,then isolate one objective-execution correction. Old
Stampede native traces contain no visible enemies during the inspected assault
and official deaths name camps. Ground-area spell coverage merits a bounded
experiment,with both seats and ordinary controls. A geometric damage estimate is
not a validated counterfactual:the isolated cast attempt returned code 18 / accepted false.
Source 20 is not implemented. Do not simultaneously change draft,timers or reserve.

Runtime/source hashes and schedules are in experiments/patch-1.0.2/;full validation
captures are preserved in the user-facing patch validation archive. Never use the
old 1.0.1 native auditor for new captures. The raw evidence directory retains its
historical1.0.1 name;actual engine pins above and per-match metadata are authoritative.

The repository now includes tools/audit_field_102.py and a standalone pinned
native decoder. Its native parity, old-engine rejection and old-replay rejection
checks pass; all 50 collected games pass summary/native per-champion validation.
