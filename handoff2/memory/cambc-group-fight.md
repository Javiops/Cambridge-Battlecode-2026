---
name: cambc-group-fight
description: 2026-10-14 "Pelea en grupo" (user's choice 09:48): group-mode ball variants all lost locally; contact-behaviour stats (we retreat, they stand); P_GROUP / P_FRONT_STAND switches
metadata:
  type: project
  modified: 2026-10-14T09:59:21.373Z
---

09:48 UTC 2026-10-14 the user chose "Pelea en grupo" on the card (team moves together and stands to cast in
fights; general, no per-map rules). Follows [[cambc-spell-gap]].

**Contact stats (online vs top 4, fight maps, rounds with an enemy within 4):** their casters stand still
46-50% (Stellar, Tavi, Cassi), step closer 22-26%, step away 20-23%; ours stand 33-39%, closer 13-17%, away
36-47%. Allies within 3 are about the same (~1) for both sides, so they are not tighter at contact, just
more aggressive. Locally v24 vs spar4: we step away 50-60%. Mode log (P_MODELOG, fbase run_game) of v24 vs
spar4 in contact rounds: farm 1245, avoid 1129, front 551, tribute 389, flee 324, fight 271: 60% of contact
we ignore the foe or back off. front_line only starts at P_FRONT_ZONE 3 with an ally within 4.

**P_GROUP T** (fbase main.cpp): T rounds after an enemy pack (P_DANGER, shared via byte 7) the team farms as
a P_BALL-style ball (P_GROUP_W, retarget every 3 rounds); P_GROUP_R R = followers walk back to within R of
the leader, the leader waits. Variants g1-g6 (T 100/300/2000, with/without P_SWEEP 5, R 4) vs spar4 on the 6
fight maps: 5-7, 6-6, 1-11, 1-11, 3-9, 3-9 (v24 7-5); vs spar6 3-9 to 5-7 (v24 7-5). Rejected: ball farming
is slower and the ball still loses the fight.

**P_FRONT_STAND** (fight.h front_line, ranged): no foe can reach us next round and the focus is within 4:
cast first (stand), then shoot. Totals vs spar4/spar6/study13/study15/ballall on the 6 fight maps (60 games):
v24 29-31, st1 (+STAND) 29-31, st2 (+P_FRONT_ZONE 4) 20-40, st3 (+ZONE 4 + P_SWEEP 5) 26-34; vs v24: st1 9-9 pool,
44-44 gen; st3 9-9, 47-41. st1 barely fires: spell hits on champions vs spar4 28 vs 27 (our ranged champions are
in farm/avoid/flee, not front, when foes come). Conclusion 10:04 UTC: no local winner; bolting one top-4 habit onto
our farm-centric bot does not help; kept v24.
