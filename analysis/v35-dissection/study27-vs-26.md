# study27 vs study26 online: the 12:37 batch dissected (2026-10-15)

Batch: 155 unranked games with study27 (= study26 + stacking up to 4 champions on camp groups of 3000+ hp) vs the
top 30, 12:37 UTC, 58-97 (37%); study26's batch at 11:33 was 59-91 (39%). Like for like on the 77 opponent-map
pairings both played: 24 vs 25 wins (8 flipped to win, 9 to loss). Same four analyses as the study26 dissection,
with study27 and study26 side by side: [positions_27.md](positions_27.md), [fights_27.md](fights_27.md),
[reactions_deaths_27.md](reactions_deaths_27.md), [farming_27.md](farming_27.md). The map mix differs a little
(elkring 9 vs 14, interlock 19 vs 13, monolith 16 vs 13) and 4 opponents changed; every per-map claim carries its count.

## Verdict: keep study27

Nothing study27 changed made anything worse, and the one thing it changed works as intended:

* The stacking fires only where 3000+ hp groups exist (rows, expanse, elkring's elk+cluster, a few on packs). On rows
  3.26 attackers per pack vs 2.66, four-stacks in 142 of 295 captures vs 18 of 285, the whole team on the first camp
  in 15/17 games; hit-to-capture on big groups 19.9 rounds vs 25.4 (median 20 vs 21); captures 17.4 vs 15.8 per game;
  gems per 100 champion-rounds 55.2 vs 49.3 (opponents 55.7); tributed 961 vs 891; we reach 1000 at r403 vs r421;
  idle streaks next to a living pack 3.9 vs 6.1 per game. Expanse's 3900-hp group gets 2.1 attackers vs 1.0.
* Costs: none measurable. Deaths 5.80 vs 5.72 per game, deaths to monsters 22 vs 25, deaths within 4 tiles of a live
  camp 45 vs 49, small-camp kill speed unchanged (17/23/24 vs 16/22/24 rounds), idle 8.0% vs 8.4%, tributes 19.6 vs 20.4.
* Everything else is the same bot within noise: fights 7.7 real per game (7.3), we open 51% (52%), outnumbered when
  opening 41% (42%), kills/deaths per real fight 0.51/0.74 (0.52/0.77), retreat at 48% hp (49), die after retreating
  19% (19%), focus 67% (66%), chase 11% (11%); hit-reaction mix within 1 point, episodes ending in death 24% (25%),
  recalls 25.6 per game with 92% arrival, help rate 49% (same); territory 85/13/1 own/mid/enemy (86/13/1), invasions
  3.0 per game (2.9), deaths 73% at home (76%), hp at first hit 91% (90%), Stellar 35% of the kills (30%).
* The 58-97 vs 59-91 is pairing noise: collision went 12-7 to 8-11 with the same fights (161-235 vs 161-212 kills) and
  the same economy curve; corners 5-12 to 8-11; packs 7-14 to 6-16; tiers 15-35 / 15-35 / 23-27 vs 10-40 / 23-27 / 21-24.

Locally study27 beat study26 154 maps to 106 on both sides; online it farms rows 7% faster and loses nothing. Keep it.

## Why rows is still 3-14 (farming_27.md, positions_27.md)

Every game ends when a team banks 1000, so rows is a race. We are now level with the opponent at r300 (685 vs 688;
study26 was 583 vs 675) and lose between r300 and r400 (940 vs 1021): 11 of the 14 losses end 957-1056, one bag short,
with 99-165 gems still in hand when their 16th bag lands (they hold 62). What happens in the last 100 rounds:

1. The four-stack dissolves after r200 (0 four-stacks in the last 94 captures): shop recalls (5.8 per game in
   r200-299) and camp respawns desynchronise the five.
2. The last bags detour through the shop: 2.0 shop recalls per game start in the final 30 rounds; Varg carries 33 gems
   for 140 rounds and buys at spawn with 99 gems at r380.
3. The r239 pack is split 33/33 between two champions; 33-gem shares are carried 60 rounds and banked as 99-gem bags
   with a 10-round channel; all rows camps are 24-36 tiles from the altar, so a capture after ~r375 cannot be banked.
4. The opponents bank 1000 at r392 median (r351-401); we gained 18 rounds with study27 and need about 15 more.

A rows end-game rule (no shop recall once either team is within ~150 of 1000, bank shares immediately, keep the four
together on the wolf nearest the altar) is worth about one bag, which is the margin in 11 of the 14 losses.

## What did not change and still decides the other maps

* Lanes 3-14: opponents squat our top clusters harder (19% of their rounds in our half vs 12%, 94 of our groups taken vs
  64) and we still keep 0.9-1.3 champions in the lane; we open only 13% of fights there.
* Packs 6-16: our own-half packs lost in 16/22 games from r289; pairs walk into groups of 3-4 one at a time.
* Monolith 5-11: 4.4 captures a game behind; opponents put 3+ on the 2700-hp wolf pairs 21% of the time, we 4%,
  because 2700 is below the 3000 threshold.
* Collision: the 108-gem 3900-hp elk cluster is still never farmed (2 captures in 19 games; opponents 1.6 a game).
* Deaths are the same bot: tribute channels never cancelled with an enemy walking in (23 deaths, 1436 gems; four of
  the five biggest single losses are tributes at collision's centre altar), melee dash into groups, casters trade at
  distance 1-2, allies next to a dying champion do not attack. The only shift: we cast on cooldown a little less
  (49% vs 55% of both-slots-up opportunities), spells come later, not fewer.
* Shop recalls from the capture tile where walking is shorter: 51% of captures, 11.4 trips a game (opp 26%, 8.6).

## Next change with the best odds, by these numbers

1. Channels and approach: cancel a tribute or recall when an enemy is closing within ~6; this is where the biggest
   single gem losses are and it is the same in both versions.
2. Rows end-game rule above (one bag = 11 of 14 losses).
3. Lower the stacking threshold to cover 2700-hp pairs (monolith, packs) and farm collision's elk cluster with the
   four; the data shows no cost to stacking.
4. Fight rules from the study26 dissection (numbers before opening, casters at 4-5) are untouched by study27.
