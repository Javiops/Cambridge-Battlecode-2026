# How the #1 farms, and how to evaluate a map from distances

15-10-2026. Ladder at 08:22 UTC: **Mite 1834 is now #1**, Univardisty 1816 is #2. I studied both.

**Data:** 101 games played today 07:00-08:28 UTC against teams ranked 1-20. Up to 6 games per team and map, each against a different rival. Every champion's captures, banking trips, recalls and deaths were decoded from the replays.

## Short answer

1. **Your cycle idea is half right.**
   - Right: each team farms a fixed set of camps on its own side, and recall is the reset. It never farms the enemy half and never touches monoliths. It rarely takes elk or gold camps.
   - Not quite: the order is not a fixed loop. Each champion picks the nearest camp that is up (or about to be), decided on the spot.
2. **Recall is a computed teleport, not only a heal.**
   - On rows, whenever "recall and walk from home to the altar" is shorter than walking to the altar, Mite recalls right after the capture. That was 53 times out of 53, carrying about 80 gems.
   - On expanse, lanes and packs it starts the recall on the capture tiles, so the 5-round recall overlaps the 5-round capture.
   - On fight maps, recall costs 22-29 steps against an 8-12 walk, so it walks to the altar.
3. **A distance-only evaluator reproduces their camp choice.** I scored each camp as `gems / (home->camp + hp/150 + 5 + bank trip)`, where the bank trip is the shorter of walking to an altar or recalling and walking from home. Taking camps on our side with a score of 0.5 or more matches Mite's farmed set on 88% of camps and Univardisty's on 84%. Guessing "never farmed" would score 71%.
4. **For our bot:**
   - study24 already scores camps this way, and its camp set and revisit gaps look like Mite's.
   - Its per-map rules only fire on the 9 known maps. Rebuilt from distances, three of them are neutral on new maps and one (bank cost) loses badly.
   - The one general habit worth copying is "recall on the capture tile". It goes into `bot/mybot_study24_caprecall.zip`.

## What the #1 does on each map (Mite)

| map | W-L here | camps used | captures/game own / middle / enemy | deaths/game | how it banks |
|---|---|---|---|---|---|
| rows | 2-4 | 3 of 9 | 15.5 / 0 / 0 | 0 | recall after every capture when the walls make it shorter, bank 1 trip per 2 camps |
| expanse | 2-4 | 7 of 30 | 28 / 0 / 0 | 0 | recall on the capture tile (half the time), else walk |
| lanes | 5-1 | 12 of 42 | 36 / 4 / 0 | 1.3 | walk to the altar next to the gem clusters, shuttle camp-altar-camp |
| monolith | 4-2 | 7.5 of 22 | 26 / 5.5 / 0 | 1.7 | walk; monoliths never taken by anyone |
| packs | 5-1 | 5 of 8 | 8.5 / 12 / 0 | 4.8 | recall on the capture tile |
| collision | 3-3 | 6.5 of 20 | 23 / 9 / 1 | 7.5 | walk |
| corners | 3-3 | 6.3 of 30 | 4 / 14 / 0 | 16 | walk; lives on the 2 gem clusters next to the centre altar |
| elkring | 5-1 | 5.5 of 10 | 22 / 4 / 0 | 7.3 | walk |
| interlock | 5-1 | 6.5 of 16 | 24.5 / 4 / 0 | 5.5 | walk |

Other habits:
- **Camp kills are fast:** 9-17 rounds per camp whatever its size, because bigger camps get more champions (2-3).
- **Revisits are not timed to respawns:** a camp is taken again 25-45 rounds after it respawns. The team is short of champion-time, not of camps.
- **Fight or farm still follows the spawn-to-spawn path.** Fight maps have paths of 26-41 and 5-16 deaths a game. Farm maps have paths of 49-85 and 0-2 deaths.

## Testing the cycle hypothesis

What fraction of next-camp choices does each rule predict? Over 2,611 choices there are about 20 candidates each, so random guessing gets 6%.

| predictor | Mite | Univardisty |
|---|---|---|
| nearest camp that is up | 38% | 41% |
| same transition as last time (their own loop) | 14-36% per map | 20-43% per map |
| same camp as 2-4 captures ago | 8-33% | 4-53% |
| best gems per round, including the bank trip | 20-24% | 21-23% |

The only fixed loop is Univardisty on rows, which alternates 2 camps. Everywhere else the plan is "this set of camps, nearest first, reset with recall when it pays".

## Turning study24's per-map rules into map evaluation

study24 has 7 rules that fire only when the map's size, altars and walls match a known map. They matter on known maps: with all of them off, study24 goes 4-14 against itself. On a new map none of them fires. I rebuilt each rule from distances (`P_FEAT`, code in `bot-feat/`) and played 88 games on 44 generated maps against study24:

| rule (known map) | distance version | result on new maps |
|---|---|---|
| bigger bag, chain camps (rows) | most own camps: recall + home->altar beats walking to an altar | 46-42, neutral |
| recall on capture tiles (lanes) | farm map with an altar within 8 of home | 44-44, neutral |
| add the bank trip to camp cost (expanse) | any farm map (path > 45) | **24-64, loses** |
| keep spell resets for live targets (corners, interlock) | path <= 45 | 45-43, neutral |

**Warning about noise:** single games flip on tiny changes. A build that only changed how much computation the first turn uses flipped 5 of the 18 official games. Differences under about 10 games in 88 are noise.

**The habit that helps everywhere** is recall on the capture tile, `P_CAPRECALL 1` on every map (study24 only did it on lanes):
- Solo farm pace against an idle rival: faster on the official maps (-65 rounds; 3 maps faster, 0 slower), on 44 generated maps (-310) and on 60 new generated maps (-194).
- Head to head against study24: 12-6 on the official maps, 45-43 on generated maps, 59-61 on the new generated maps.
- Against the three sparring bots: 46-8, where study24 goes 47-7.
- Zip: `/mnt/project-files/bot/mybot_study24_caprecall.zip`.

## How to evaluate an unseen map (the recipe)

At game start, compute from distance fields:
1. **Spawn-to-spawn path d:** 41 or less means a fight map (caster draft, fight rules); 49 or more means a farm map.
2. **Every camp:** its distance from our spawn and from theirs, and its bank trip (`min(walk to altar, 5 + home->altar)`).
3. **Farm set:** camps closer to us than to them, with gems, not monoliths, scoring at least 0.5 with the formula above. Middle camps next to an altar are worth contesting.
4. **Banking:** after a capture, recall when `5 + home->altar` is shorter than the walk (rows-type walls). Start the recall on the capture tiles when a recall was coming anyway.
5. **Inside the set:** go to the nearest camp that is up, and do not plan a fixed order.

## Files

- `scripts/`: replay decoding (`compact.py`, `events.py`, `legs.py`), the analyses (`deposit*.py`, `choice.py`, `score2.py`, `revisit.py`, `groupset.py`, `killspeed.py`), the evaluator (`evaluator.py`, `setpred.py`, `geo.py`), and the arena helpers (`pacecmp.py` for solo pace on 113 maps, `ab.sh` for head-to-head with the sign test, `vary.sh`).
- `data/`: the selected matches, every decision with its candidates, and compact per-round tracks (`compact.tgz`).
- `maps_gen4/`: 60 new generated maps (seed 77) used as an extra unseen set.
- `bot-feat/src`: study24 with the `P_FEAT` / `P_FR_*` / `P_BANKX` switches. All are off by default.
