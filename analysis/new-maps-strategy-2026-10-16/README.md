# New site maps: strategy per map (2026-10-16)

The same method as the first two days for the nine original maps, applied to the eight maps the site added on 16 Oct
(ambush, contest, eight, fragment, pilgrimage, rushbait-v2, stampede, swirl). For each map: what the top-10 winners do
(120 top-10 replays from the morning study), what we do (online since 08:00 and local games), the rule, and its local
numbers. Rules are chosen from map features, never map names (`bots/newmaps/src/mapplan.h` on branch
`claude/new-maps-strategy-5ffnvq`).

**Judge.** The five specialists of `tools/panel` (built from the v51 zip), each of the 17 site maps from both sides,
so 10 games per map and 170 per bot (`python3 tools/nm/permap.py bots/BASE bots/CAND`). Generated maps (hold60,
dev200) are the second check. Recompiling the same code moves ±5-9 of the 170 games (fuel), so only a gain above that,
or a per-map gain that also holds on the generated maps, counts.

## Fight map or farm map

The old rule said a map is a fight map when the walking path between the spawns is 45 tiles or less. That misses
four new maps: the top 10 fight on eight (path 46), stampede (55), pilgrimage and ambush (123) and draft casters there.
What those maps have in common is **few altars (1 to 4) with 5 champions a side**: everyone banks at the same few
places, so the teams meet there. The old farm maps with 5 champions have many altars (lanes 18, monolith 6).

| map | champs | altars | spawn path | type for the top 10 | top-10 draft | ours online | online 08-18 UTC |
|---|---|---|---|---|---|---|---|
| eight | 5 | 1 | 46 | fight at the one central altar | C&I, Stellar, Ren, Varg, Ryth/Tavi | Vendetta Varg C&I Ryth Tavi | 1-84 |
| pilgrimage | 5 | 4 | 123 | farm + fights in the middle | C&I, Stellar, Varg, Tavi/Ryth, Ren | same farm draft | 14-77 |
| contest | 5 | 2 | 39 | gold, then a fight for the monolith | C&I, Stellar, Tavi, Ren + Prism/Varg | Ryth Stellar Prism Ren Tavi | 19-72 |
| stampede | 5 | 2 | 55 | gold first, centre jackpot from r350 | C&I, Stellar, Varg, Tavi, Ren | farm draft | 24-67 |
| ambush | 5 | 4 | 123 | farm race (1.4 kills a game) | C&I, Stellar, Varg, Tavi/Ryth, Ren | farm draft | 25-65 |
| fragment | 3 | 2 | 23 | fight, few gems | C&I, Ren, Stellar | same | 35-56 |
| swirl | 4 | 2 | 13 | fight from r7 | C&I, Stellar, Ren, Tavi | same | 36-53 |
| rushbait-v2 | 4 | 2 | 1 | farm race in the middle | C&I, Stellar, Ren, Varg | same | 44-39 |

## Map by map

Zones are thirds of the spawn-to-spawn axis (own / middle / enemy), from `zones.md` (top 10) and our local games.

**stampede.** Top winners stay off the 360-gem centre until r350-475, farm 9100 gold (56 gold captures) and buy 50
times, then take the centre by force (16 kills, 6 deaths). Already coded as P_JACKPOT 350 + P_JACKGO 350 (in v52). What
was missing was the draft: with the farm draft we lose the centre fight. **Rule 1 (draft)** 5 → 9 of 10 on v51.

**pilgrimage.** Winners live in the middle third (73-80% of the time), capture the middle camps 15 times a game and die
3.9 times; we did the same route but died 16 times in the middle. **Rule 1** 6 → 10 of 10 (deaths 18.8 → 10.0).

**eight.** One altar, in the centre. Winners bank there 19 times a game (bag 44), capture the two wolf camps next to
it and fight for it (14 kills, 10 deaths). We stayed in our third (92% of the time), banked 5 times, and died 11 times
at home. **Rule 1** 5 → 6 of 10. The rest is fight execution at the centre: we still die 13-15 times a game locally.

**ambush.** A farm race on a 100x100 map. Winners take the 106-gem camp at r75 and the 72-gem camp next to it at
r107, bank 106-120 gems a trip and reach 1000 gems at r603; we took the first camp at r86, came back for it at r191,
banked 53 a trip and reached 1000 at r702. Rule 1 is neutral here locally (9 → 8 of 10). With the caster draft, our
Cassi&Issac take the elk camp as a pair and the elks focus Issac: 48 deaths to camps in 6 local games (34 before r300),
26 with the old draft. See the candidates below.

**contest.** Only a 200-gem monolith (respawn 150). Winners farm 11 700 gold first (79 gold captures, 73 buys) and get
their first gem at r1234. P_MONO (in v52) does this; locally we win 9 of 10 on v51, 6 of 10 on v52. Online we lose by
dying (about 19 deaths before r500), which the local panel cannot reproduce. The top 10 always have Cassi&Issac here;
putting them in our contest draft lost locally (9 → 4), so it stays an online test idea, not a rule.

**fragment.** 30x30, 3 champions, only 204 gems on the map, so camps are taken again on respawn. Same draft as the
winners; they capture the central camp 8.5 times a game and die 7 times, we 2.5 times and 15-17 times. Fight execution.

**swirl.** 4 champions, contact at r7, 1728 gems. Winners hold the middle (14 middle captures, 9 deaths); we die 18-31
times. Fight execution. Note: on v52 swirl is 2 of 10 locally; with P_ALLYDUTY off it is 7 of 10 (sent to the fixes thread).

**rushbait-v2.** The spawns touch, every camp is in the middle third, almost no fights (2 kills). It is farm speed:
winners 41.5 captures, us 38.7. Our best new map online (53%).

## Rules

**Rule 1, draft (P_MAPPLAN 1, P_MP_DRAFT 1). In v52.** 5 champions, spawn path > 45, at most 4 altars: draft
Cassi&Issac, Stellar, Varg, Tavi, Ren. It fires on stampede, pilgrimage, eight and ambush, on none of the old maps.
On v51: site maps 121 → 129 of 170 (9 games flipped to wins, 1 to a loss); hold60 + dev200 flips 24-6. Our other
fight draft (Ryth, Stellar, Prism, Ren, Tavi) did as well on site maps but lost 5-10 on hold60.

**Candidates that did not clear the noise (switches in `bots/newmaps`/`nm2`, all off):**

| switch | idea (from the top 10) | site maps | where it moved |
|---|---|---|---|
| P_BALL 5 | move as one group | 132 → 119 | fragment +3, eight +2, rushbait +2; ambush -4, contest -6; dev200 57-104 |
| P_TRIBUTE_GEMS 40 | eight winners bank 44 a trip | 132 → 127 | eight +2; lanes -3, rushbait -2 |
| P_HOLD 400 | hold the centre altar | 132 → 119 | contest 9 → 1 |
| P_MP_OPEN 500 | rule 1 not on very open maps (ambush) | 120 → 120 | ambush 1-1 |
| P_MP_FARHOME 60 (+chain 130) | take a second camp before banking on far maps (ambush) | 122 → 121 (116) | ambush -3 with chain 130 |
| P_MP_FOCUS 100 | elk camps focus one champion: size the squad for one body | 122 → 121 | ambush deaths 9.6 → 0.5, swirl +4, stampede +2; interlock -4, packs -3 |
| P_MP_CAMPAVOID 1 | walk around awake camps we are not fighting | 122 → 121 | fragment +4, swirl +3, elkring +2; monolith -3, rushbait -2 |
| P_NOGOLD 0, P_SHOP_GOLD 150, P_JACKGO 280, P_JACKN 5 | gold, shop, centre timing | no gain | |

P_MP_FOCUS is the one worth an online look: it nearly removes our camp deaths on ambush, which is a real bug, but the
panel cannot see the farm-speed gain there.

## Tools

- `tools/nm/permap.py` per-map panel table with flips (shares `out/ab-cache`).
- `tools/nm/localzones.py` where our bot plays in local games (zones, captures, banks, opening, gems at r300/r500).
- `tools/nm/campdeaths.py` deaths with no enemy within 7 tiles (killed by a camp), per champion.
- `scripts/zones.py` the same zone table for the top-10 replays (`zones.md`); `map_features.json` features of all 277 maps.
