# How our bot plays: dissection of v35 (study26) in 150 online games (2026-10-15)

The games: 150 unranked challenges started 11:33 UTC with the active bot (v35 = study26) against the top 30 of the
ladder (5 maps each; we are side a in 145 of them). Record 59-91 (39%); vs the top 10 10-40, vs ranks 11-30 49-51.
Every replay was decoded step by step (`data/steps.tgz`, format in `data/DATA.md`, game list `data/selected.json`)
and four analysts measured one topic each, always counting the same thing for us and for the opponent in the same
games, with Mite's numbers from the #1/#2 dissection as the second reference:

* [positions.md](positions.md): territory, formation, what each champion does each round, camps held, loss maps
* [fights.md](fights.md): who starts fights, how, focus, spells, ranged distance, how fights end
* [reactions_deaths.md](reactions_deaths.md): what we do when hit, retreats, recalls, help, all 858 deaths
* [farming.md](farming.md): economy curve, draft, shop, camp set, squad size, bags, tributes, lost time

Scripts in `scripts_*/` (python3 -I, loaders in each `common.py`).

## 1. The one-paragraph answer

The farm engine is not the problem: alive, we capture as often as the top teams (1.19 vs 1.21 captures per 100
champion-rounds), with the same gems per capture (35), same bag size (median 44), straighter walking (0.89 vs 0.84),
less idling (8% vs 10%). We lose because we die: 858 deaths vs 581 (5.7 vs 3.9 per game), 13.6% of our champion-rounds
spent dead vs 9%, 73-76% of those deaths in our own half, from 90% hp, over ~5 rounds, to spells. The deaths come from
how we behave around enemies: we keep farming or stand still while an enemy pack walks into range (contact lasts a
median 13 rounds before the first hit, and in those rounds we farm 23% of the time, idle 16%, move away 10%), we open
fights at a disadvantage (outnumbered within 6 in 42% of our openers, allies more than 8 tiles away in 85%), our
ranged champions fight from distance 1-2 (35% of their basic attacks vs 24%), we retreat at 50% hp one tile per
round with the attacker adjacent and die after retreating twice as often (19% vs 11%; casters 30% vs 13%), we never
cancel a tribute or a recall under fire, and allies next to a dying champion keep farming (325 of 709 deaths had an
ally within 6 that never attacked). We also never defend territory: opponents cross into our half 11.9 times a game
(we 2.9), capture camps in our half in 42% of games, and 56% of our champion-rounds while an invader stands in our half
are spent more than 8 tiles from it.

## 2. Positions and map control (positions.md)

* Territory: 85-90% of our champion-rounds in our own half, 0-2% in the enemy half, all game. Opponents: 8-11% of their
  rounds are in OUR half from round 50 (corners 14-26%, lanes 12-20%), 11.9 crossings a game to our 2.9 (ours are chases,
  78% start with an enemy within 8). They capture 166 groups on our side of the map in 150 games, we capture 52 on theirs.
* No defence rule: with an invader in our half (17,064 rounds), near it we move 52%, stand 12%, hit camps 9%, recall 7%,
  fight 10%; 56% of our champions are more than 8 tiles away. Lanes: they put 4-5 champions on our top clusters from
  round 60 and squat 100+ rounds; we keep 1.2-1.4 champions in that lane and lose 3-15.
* Formation: pairwise distance 10.6 (opp 11.5), largest cluster 2 champions, 29% of rounds with no ally within 6
  (opp 32%): we are not more split than they are. But casters are not behind the melee: melee strictly in front only
  44% (opp 50%, Mite +1.35 tiles).
* Mid-camp balance decides games: when the opponent takes 6+ more middle camps than us we win 0% (n=18), equal 38%,
  we take 6+ more 87% (n=16). Corners: we win the round 0-49 centre clearing 34-8, then lose the centre from round 100
  as dead champions return one at a time.
* Our positional numbers are identical in wins and losses on every map; what differs is deaths (corners 6.6 vs 16.4,
  collision 7.6 vs 17.7) and the opponent's share of time in our half.
* Opening is scripted (1-2 position patterns at r10-40 per map; opponents 13-21). Rows: Cassi stands at (36,8) r203-233
  in 15 of 18 games; 6.1 idle streaks a game next to a living own camp (opp 1.3), 10.7 rounds each.

## 3. Fights (fights.md, 2158 fights, 1096 "real")

* Volume and openers match the top 2: 7.3 real fights per game (Mite 7.2), we hit first in 52% (Mite 54%), the opener
  is a spell 89% of the time at distance 4, first victim isolated 56%.
* We lose the exchanges: 0.52 kills / 0.77 deaths per real fight (Mite 0.67 / 0.68); vs the top 10 0.44 / 0.92.
  Opponents opening on us: 0.97 kills / 0.32 deaths (n=521); us opening: 0.69 / 0.58 (n=575). Our openers on a walking
  enemy (59% of them) are a net loss; only openers on an enemy that is farming, recalling or tributing pay.
* Numbers: we open outnumbered within 6 in 42% of our openers (opp 26%), outnumbering in 23%; the opener is alone
  within 6 in 54%; allies >8 away in 85%. Hp is not a criterion. We open more when behind (67%) than when ahead (38%).
* When they open: 54% in our half, 15 tiles from our spawn, 33% within 3 of an altar; we are split 83%, carrying gems
  50% (mean 48). The enemy was within 8 for 8+ rounds before the hit in 68% of cases (median 13 rounds); in those
  rounds we farm 23% of champion-rounds (opp 14%), idle 16%, move away 10%, move closer 49%.
* Focus 66% same victim when 2+ hit (opp 74%); nearest 72%; chase >= 3 steps 11% (same as everyone).
* Spells: cast within 2 rounds of contact 79%; 79% of our champion damage is spells (Mite 62%): we are a spell team.
* Ranged distance is the biggest micro gap: 35% of ranged basic attacks at distance 1-2 (953/2752) vs 24%; 36% of
  spells from 1-3 vs 22%; only 8% of spells at 5+ vs 17%.
* Fights: median 4 rounds, end by walk-away 56%, kill 16%, wipe 14%, recall 13%; who leaves first is symmetric.
  Retreat under fire at 49% hp (opp 47%, Mite 38%), but we die after the retreat step 19% vs 11% (casters 30% vs 13%)
  because we are at distance 1-2 when we decide.
* Per map: corners (21 fights a game, we lose kills 121-231) and packs (75-144) bleed; elkring is the only map where
  we win trades (102-80). Per opponent: VeryGood 1-31, Intercontinental Fish 6-52, Univardisty 6-35, Conley 7-41.

## 4. Reactions, retreats, recalls, deaths (reactions_deaths.md)

* The hit reflex is the same as the opponents' (fight back 32%, move away 15%, closer 13%, nothing 20%); the outcome is
  not: 25% of our hit episodes end in death (717/2866) vs 13.7% (474/3450). First retreat step 2 rounds after the first
  hit for both sides. Melee step closer on the first hit (Vendetta 51%, Ryth 35%, Issac 30%); Tavi does nothing 43%.
  17% of melee hit-rounds are a melee standing still with the attacker 2+ tiles away (5-round idle streaks under fire:
  59ac9626 r182-186, cabfadde r251-255).
* Retreats (1775): start at 54% hp with the enemy at 3; followed 76%; after 5 rounds we outrun it 46% (opp 60%); toward
  spawn 53% (opp 63%); outcome death 26% / recall 37% / escape 27% (opp 13 / 47 / 28). Retreats below 40% hp die 40%
  (opp 17%). Retreat alone 31%, allies stay 45%, all retreat together 14%.
* Recalls (3860, 25.7 a game): 91% arrive; 71% start with nobody within 9 (shop trips and heals, not escapes); after an
  interruption we retry 32% (Mite 59%), fight 50%, die 15%. Corners: 72% arrival, 83 interruptions + 34 deaths in channel.
  0 voluntary cancels; tributes are continued under fire (17 deaths during tribute channels, 724 gems; ae2470ab Cassi
  restarts a tribute at 14% hp with 146 gems and dies).
* Help: an ally within 8 fights 29%, comes 20%, keeps farming 12%, moves away 15%; an ally that was hitting a camp
  keeps farming 46%; help rate 32% when the victim dies vs 54% when it survives (opponents the same). In 325 of our
  709 direct deaths an ally within 6 never attacked.
* Deaths: 858 (5.72 a game; opp 3.87; Mite 4.9, Univardisty 6.1), 8586 gems lost (57 a game, 7.1% of tributed). 73% in
  our own half, median 14 tiles from spawn. Before the fatal episode: approaching the enemy 38%, fleeing 20%, idle 12%,
  farming 9%, fighting 8%, recalling 5%, tributing 3%. Hp at the first hit 90% median (501/709 at 70%+). Killers:
  Stellar 211 (30%), Tavi 80, Ren 75; spells 68% of the damage. 1 foe did all the damage in 289 deaths, 2 in 255.
  Per type: Stellar 1.95 per game drafted, Prism 2.55, Tavi 1.37. Corners 13.5 deaths a game, collision 7.9, elkring 6.5,
  packs 5.1; expanse/rows 0.
* The deciding deaths (10 worst games, 232-376 gems each) are three patterns: a caster killed during a tribute channel
  with enemies walking into range 4; a melee walking or dashing into a group at full hp; a champion standing still while
  poked from range 3-4, then recalling at distance 3. In all 20 narrated deaths the enemy was visible 3-5 rounds before
  the first hit; an ally attacked in only 6 of 20.

## 5. Farming cycle and economy (farming.md)

* Alive, we keep pace: captures per 100 champion-rounds 1.19 vs 1.21, gems per capture 35 vs 35.5, damage per attacker-
  round equal or higher, walking efficiency 0.89 vs 0.84 (Mite 0.75), idle 8% vs 10%, gold unspent at the end 18 vs 58.
  Expanse (0 deaths both sides) is a tie, 72 vs 70 gems per 100 champion-rounds, 11-6.
* Curve: ahead at r100 on collision/corners/expanse/monolith/rows, behind from r150-250 on corners, elkring, lanes,
  packs, rows. Median decided round 250; 30 games decided by r100. In losses we drop 9% of our gems at death vs their 2%.
* Draft fixed per map (150/150); shop = melee power x5, durability, jungle, bruiser; casters power focus, durability;
  Tavi buys nothing in 16/75 games; never a monster emblem (opponents' melee buy one in 25-64% of games; Mite jungle first).
* Camps: 19.8 own / 4.4 mid / 0.3 enemy captures a game (opp 21.2 / 4.4 / 1.1); fixed set and scripted order on 5
  maps; nearest-camp-up chosen 44% (opp 52%). Camps they farm and we never touch: collision's 108-gem elk cluster (opp
  1.16 a game, us 0.05), lanes' own elk and mid wolves (+2.9 captures a game for them), corners' far wolves.
* Squad size: attackers by camp hp bucket 1.16 / 1.51 / 2.03 / 2.57 (opp 1.44 / 1.82 / 2.27 / 2.69; Mite 2.0 / 2.05 /
  2.4 / 3.5); hit-to-capture 16 / 22 / 24 / 21 rounds (Mite 12 / 17 / 21 / 23); 60% of 800-1500 hp captures are a
  single attacker (49%); first camp gets 2-3 of ours vs 3-5 of theirs, so our first capture is 5-15 rounds later on 5
  maps. Ranged helpers stand off the capture tiles and are unpaid in 53-66% of the kills they help (Tavi 224 vs 501 gold
  a game); rows Cassi earns 0 gems for 225 rounds in every game.
* Recalls after 50% of captures (opp 26%): 48% shop trips (median 180 gold), 46% heals; only 1% true teleports. On
  elkring (86%), monolith (83%), interlock (62%) the recall replaces a shorter walk to the altar: 1143 recalls started on
  the capture tile when walking was shorter, 75 champion-rounds a game vs 31.
* Time dead 13.6% vs 9.0% of champion-rounds (corners 27%, collision 22%, packs 19%). Rows (0 deaths, 4-14) isolates the
  engine gap: same set, same bags, same kill time, but 4.7 of theirs on the first camp and a steady 2.1-2.5 captures per
  50 rounds vs our bursts (identical in all 18 games), 891 vs 1034 tributed.
* Costs in gems a game: time dead +41 (+43 dropped at death in losses); shop recalls before tributing +32 (interlock
  +170, elkring +100); squad size / first camp (packs -170, lanes -110, rows -92); camps left to them (collision 125,
  lanes 110, corners 50); unpaid ranged helpers.

## 6. The rules a replay reader would write down for v35

1. Draft fixed per map; opening scripted per map (same tiles every game); camp set fixed, nearest camp up, 1-2 champions
   per camp, one capturer; recall after half the captures to shop or heal, also where walking is shorter.
2. Stay in our half; cross only to chase; no defence of our half, no regrouping, no reinforcing a lane.
3. On an enemy in sight: keep doing the current job (farm, tribute, recall) until hit or until it is in spell range;
   then cast at 4 on the nearest enemy, regardless of numbers or hp, alone if alone.
4. Ranged champions walk to distance 1-2 and trade there; melee step in on the first hit; casters stand and cast.
5. Leave at ~50% hp, one tile a round, towards spawn, alone; recall from distance 3-6 while followed; no retry.
6. Never cancel a channel; allies that were busy stay busy.
7. Return to the fight one by one after respawn.

## 7. Where the gems go (what would change the result, in order of size)

1. Deaths (5.7 a game): the three patterns in section 4 are all "enemy visible for 3-13 rounds, we did nothing
   different". A rule that reacts to an enemy pack within 8 (stop channels, pull casters back to 4+, group within 3,
   retreat together at 60%+) addresses 73% of deaths that happen at home.
2. Opening fights only with numbers: 42% of our openers are outnumbered and they convert at 0.69/0.58; theirs at
   0.97/0.32. Opening on an enemy that is farming, tributing or recalling is the only opener that pays.
3. Ranged distance: casters at 4-5, not 1-2 (953 of 2752 basic attacks at 1-2).
4. Territory: answer invaders with numbers or leave the lane; take the middle camps (mid-camp balance predicts the
   result 0% to 87%).
5. Farm engine: 2 attackers on every camp and 3-5 on the first one (Mite's rule, already in study27's stacking),
   no recall before tributing where walking is shorter, let ranged helpers stand on the capture tiles.

These are measurements of study26; study27 (stacking on big camps) is active since 12:08 and the loop is collecting its
games the same way, so the same scripts can be re-run on it (`scripts_*/`, with a new `selected.json`).

## Update: study27 (the 12:37 batch, 155 games) and study28

[study27/README.md](study27/README.md) repeats the four analyses on the next version (study27 = study26 + stacking up to 4
champions on 3000+ hp camps) side by side with study26: stacking works on rows and costs nothing, everything else is the
same bot; the verdict was keep study27. From that evidence, study28 (PR #6, merged) adds one rule: cancel a tribute or
recall when the enemies walking in would deal 60% of our hp before it ends (locally 24-5 maps on dev200 vs study27). The
other five ideas (react to a pack before the first hit, open only with numbers, ranged at 4+, rows end-game, stacking
threshold 2700) were coin flips locally and stay off in `params.h` with their numbers.
