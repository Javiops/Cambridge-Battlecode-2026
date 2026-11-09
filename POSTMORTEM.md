# Postmortem: Live Love Larp, Cambridge Battlecode 2026a

Written 9 November 2026, after the 4 November international qualifier and before the 18 November finals. Every
number below comes from our own measurements during the competition (replay decodes, online match groups, local
arenas) or from the public ladder. Where a number is an estimate, it says so.

## Contents

1. [Summary](#1-summary)
2. [The game, briefly](#2-the-game-briefly)
3. [What we built](#3-what-we-built)
4. [How we worked](#4-how-we-worked)
5. [Timeline](#5-timeline)
6. [Why we lost: the diagnosis](#6-why-we-lost-the-diagnosis)
7. [What worked](#7-what-worked)
8. [What did not work: the candidate ledger](#8-what-did-not-work-the-candidate-ledger)
9. [Why our measurements failed us](#9-why-our-measurements-failed-us)
10. [Process mistakes](#10-process-mistakes)
11. [Comparison with the top and with our peers](#11-comparison-with-the-top-and-with-our-peers)
12. [Lessons, and the plan we would follow next time](#12-lessons-and-the-plan-we-would-follow-next-time)
13. [Open questions](#13-open-questions)

---

## 1. Summary

**Result.** We did not reach the finals. Our goal was the top 10. Our best recorded ladder rank was 52nd
(24 October). On 8 November we were 125th of 826 with a rating of 1925, 87th in the international category. Only
the top 8 international teams went through the 4 November qualifier.

**Where the final bot stood.** v21, live from 30 October, won **7 of 80** games against ladder ranks 5 to 20. Against
those teams the gap was large in every economic measure. Rivals earned 6,919 gold per game to our 3,537 and
collected 1,130 gems to our 556. Their Heart of Ruin did 19.3k monster damage per game to ours 7.5k, and died 0.72
times per game to ours 3.44.

**Thesis.** We did not lose because of one missing rule, and not because we fought worse in even fights. We lost
because **our champions were alone, and so outnumbered, when contact happened.** From round 150 on, the rival
brought fights into our half and we died there two to three times as often as they did. Every death cost about 53
rounds of a dead champion, the gems in the bag, 100 gold for the killer, and the items that gold would have bought.
That snowball, not farming technique, was most of the economic gap.

We diagnosed this correctly by 18 October and kept confirming it until the end. **We never fixed it**, because:

- **We attacked it with single-rule patches.** "Retreat when outnumbered", "walk with an ally", "join a fight",
  "defend our half": each one moved its own metric a little and none moved wins. The cause was a team-formation
  property that needed a design from the draft onward.
- **Our local judge could not see fight changes.** For about two weeks our online judge could not separate a real
  +5% change from noise either. We made dozens of decisions on numbers that meant nothing.
- **We changed method five times in three weeks.** Each new method threw away most of the work before it.

The improvements that held were bug fixes, fuel fixes and changes that made us die less directly. Together they gave
the one large rating jump of the season, +207 in two days (21 to 23 October).

---

## 2. The game, briefly

Two teams draft 3 to 5 champions from a pool of 12. Champions farm neutral camps (wolves, elk, gem and gold clusters,
golems, 20,000 hp monoliths) for gems and gold. Gems count only once a champion carries them to an altar and
channels a tribute of ceil(bag/10) turns. A champion who dies drops the whole bag to the killer, who also gets 100
gold. A dead champion is out for 60 rounds. The first team to bank 1000 gems wins; at round 2000 banked gems, then
lifetime gold, break the tie.

What shaped the engineering:

- **No shared brain.** Each champion runs its own copy of the bot and sees only its own vision. The team shares 8
  bytes of memory for the whole game, plus 1024 bytes written during the draft.
- **Fuel.** Each turn has 100,000 units of fuel, roughly WASM instructions. A trivial C++ loop costs about 10 fuel
  per iteration and one `printf` about 570. A turn that runs out is suspended mid-code and resumed next round, so
  expensive planning costs actions.
- **Determinism.** The same two bots on the same map and sides always play the same game. We found this out on
  24 October; it mattered a lot more than we realised at first (section 9).
- **Patches.** Three balance patches in week 2 and patch 2.0.0 on 25 October. That patch rebalanced every
  champion, added emblem families, cut the camp economy and grew the map pool from 35 to 70 maps.

---

## 3. What we built

### The final bot, v21

`bots/live-love-larp/src/`: 8,859 lines of C++20, 249 `P_*` switches in `params.h`. It is the unchanged source of
the zip that was live on the site as version 212.

| Part | What it does |
| --- | --- |
| Draft (`main.cpp`) | Reads the map in the draft turn. Default 5-pick roster Heart of Ruin, Vesper, Marcella, Ryth, Vendetta, copied from the top-10 picks of 22 October; on far maps (spawn-to-altar path 60 or more) Heart of Ruin is swapped for a far-map pick |
| Farming | Camp groups claimed through shared memory. A capture is split between every ally on the reward tiles, so one champion captures and the rest move on |
| `plan_t10.h` | Per-map, per-50-round table of which camp groups top-10 winners spent time on, from about 600 top-10 vs top-10 games; it multiplies our target scores from round 150 to 650 |
| Roles | Escorts follow the carry (Heart of Ruin with Vesper, Ryth with Marcella) on near maps |
| Fights (`fight.h`, `verdict.h`, `bcfight.h`) | First-contact verdict from a two-sided damage model; kiting for casters; focus on one target; flee rules when outnumbered |
| Heart of Ruin (`heart_of_ruin.h`) | v21's own change: self-shield whenever ready in combat. Our shield output was 5.2k per game against the rivals' 16.9k |
| Banking | Altar choice that does not switch mid-walk (bank-v1b) |
| Fuel | A deterministic fuel meter (`fuel_okc`): heavy passes are charged a fixed price, so a code change elsewhere does not change decisions |
| Champions | One header per champion (`<champion>.h`) with its shop plan and special rules |

### Lineage

v3 (13 Oct) → study22-28 (14-15 Oct) → v44 genetic fight parameters (16 Oct) → teammate base v52 → **v53** (16 Oct,
fight verdict + fuel fix) → bank-v1b, recall escape, team fight (18-19 Oct) → v94-v98 (goldval, horfocus) → V13
stallfix (22 Oct) → V20 one header per champion (23 Oct) → **kvvl** (v164, deterministic fuel, 24 Oct) → e1foco
(27 Oct) → top-10 plan line t10plan-v2 to v21 (27-30 Oct) → **v21** (30 Oct).

The site numbered submissions, not versions: v21 went live as site version **212**. That number is the clearest
measure of how many uploads we made.

---

## 4. How we worked

### People and agents

A small team with one main developer, working mostly through Claude Code sessions: about 80 project threads by
25 October, each owning one line of work (fights, farm, shop, deaths, the online loop, audits). One Windows PC ran
local arenas and, later, the online loop. A coordinator session dispatched work between threads.

### Local testing

- **Arena.** `cambc run` in parallel over 9, then 17, 35 and 70 official maps, plus 44 generated maps, 60 sealed
  hold-out maps and 200 development maps. One local game took about 1.4 seconds. 140 games (70 maps × both sides) took
  about 2 minutes with 4 jobs.
- **Sparring bots.** Caster bots (spar11/12/16), hunters (pHuntF), "ghost" bots that replayed a top team's recorded
  route, and a rival panel of other teams' drafts.
- **Gates.** `gate.py` with stages (safety, fresh maps with early stopping, caster panel, counter-examples) and
  later the J2 and "hard panel" judges.

### Online testing (from 15 October)

- The site allowed unranked challenge groups of 5 maps: 30 groups per team per rolling hour (150 games), later 50.
  The challenger was always side A, and the site always played our **active** submission. Testing a candidate meant
  making it the live bot for one batch, then switching back.
- **The judge evolved four times.**
  1. Win rate on changed games, more than 57%.
  2. From 18 October, (for − against) ≥ 2·√(changed games), plus a check that our final score was not lower in
     clearly more pairs.
  3. From 19 October, a two-step judge with no order bias.
  4. From 25 October, the candidate alone replayed on the exact pinned groups of the base, against the 15 teams just
     above us, later ranks 5 to 20.

---

## 5. Timeline

### Rating (public ladder samples)

| Date | Rating | Event |
| --- | ---: | --- |
| 13 Oct | 1500 | First upload (v3) |
| 15 Oct | 1618 | study26-28, top-2 dissection |
| 16 Oct | 1669 | Genetic fight parameters (v44), then teammate base |
| 18 Oct | 1728 | v53 base; online judge becomes the main judge |
| 19 Oct | 1652 | Recall escape and team fight; week-2 balance patches land |
| 21 Oct | 1649 | Low point |
| 22 Oct | 1846 | goldval (v96), horfocus (v98), stallfix (V13) |
| 24 Oct | 1862 | Best recorded rank, 52nd (on 24 October) |
| 26 Oct | 1875 | Patch 2.0.0; ladder reshuffles |
| 27 Oct | 1828 | |
| 31 Oct | 1876 | v21 live since 30 October |
| 2 Nov | 1902 | User stops development |
| 4 Nov | 1908 | International qualifier |
| 8 Nov | 1925 | Ladder still open; no longer counts |

### Phases

| Dates | Phase | What we did | How it ended |
| --- | --- | --- | --- |
| 13-14 Oct | First bot and switches | C++ bot; top-5 and top-10 replay studies; each top-team habit coded as a `P_*` switch | Many won locally and lost online. P_HOLD (hold the centre) won locally and went 0-7 online on corners and collision |
| 15 Oct | Top-2 dissection | Decision-by-decision study of #1 and #2 over 101 games; study26 to study28 | Their edge was dying less, not fighting better. study28 went 24-5 locally and was flat online |
| 16 Oct | Genetic algorithms, DQN, imitation | 7 cloud islands plus the PC; a 25-32-7 Q-network; cloning the #1 team's fights | All dropped by the evening. The genetic "champion" was selection luck |
| 16-17 Oct | Teammate base, v52 to v59 | Behaviour fixes on the teammate's bot, first-contact verdict, two-sided fight model, wards | v53 became the base. v54 to v59 were rejected online; lanes collapsed from fuel overruns caused by wards |
| 17-18 Oct | From-scratch lab | New layered bot following a published top player's method, with a local league | core-v57 ranked 27th of 28 against our own old bots. Back to v53 |
| 18-24 Oct | Online loop on v53 | Candidates on defence, banking, micro, kills, finishing, draft, duels, shop, farm | A handful passed. On 24 October, 16 online slots and none passed |
| 24-27 Oct | Deterministic base | kvvl (deterministic fuel); patch 2.0.0; farm pricing, superiority and shop lines | All closed: nothing passed online |
| 27-30 Oct | Copy the top-10 plan | Per-map plan and escort roles from 600 top-10 vs top-10 games, then t10plan-v5 to v31 | v21 passed over 400 games and went live on 30 October |
| 2-4 Nov | End | Development stopped on 2 November; qualifier on 4 November | Not qualified |

---

## 6. Why we lost: the diagnosis

The same picture came back from every study, with every base, against every rank band.

### 6.1 We died more often, not differently

v53 against the top 30, 1,562 online games (18 October), in our losses:

| Per game | Us | Rival |
| --- | ---: | ---: |
| Entries into the other half | 5.8 | 16.5 |
| Deaths | 9.1 | 3.9 |
| Kills | 2.7 | 7.2 |
| Share of our deaths on our own half | 70% | |

How deaths happened was the same as theirs: the shares by spell, while fleeing and while alone matched. We simply
accepted, or failed to avoid, the fights they brought to our camps from round 150 on.

Death census against the top 10 (67 games of v65, 18 October), deaths per game:

| Situation | Us | Them |
| --- | ---: | ---: |
| Running away | 2.57 | 0.63 |
| Channelling a recall or tribute | 1.42 | 0.22 |
| Walking | 1.30 | 0.54 |
| Fighting, not outnumbered | 1.21 | 0.34 |
| Hitting a camp | 0.84 | 0.10 |
| **Total** | **8.78** | **2.69** |
| On our own half | 5.28 | 1.04 |

### 6.2 Damage was equal; conversion was not

- **677 fights against the top 10 (18 October).** We dealt the same damage and brought them low as often as they did
  us. But when one of ours dropped below 45% hp it died **48%** of the time; one of theirs, **11%**.
- **Finishing.** A low rival next to us died 9% of the time; a low one of ours next to them, 40%.
- **Escaping.** When low, they recalled 41% of the time and died 1% of the time; we recalled 23%.
- **Conversion against our own band (v72, 19 October).** We died 0.96 times per 1,000 damage taken, they 0.42.
  Same damage per contact round, same number of drops below 50%.
- **v17 against ranks 5-20 (29 October), champion-killed deaths in rounds 30-300 by numbers within 6 tiles:**

| Per game | Us | Rival |
| --- | ---: | ---: |
| Outnumbered (foes > allies + 1) | 1.30 | 0.35 |
| Even | 0.72 | 0.34 |
| Ahead | 0.25 | 0.33 |
| **Total** | **2.27** | **1.01** |

Stats at round 300 were close (max hp 1249 vs 1360, strength 60 vs 64, items 2.3 vs 2.9).

### 6.3 The root: formation before contact

- **Who has more champions at the fight.** The top 5 had 4.0 to 4.9 outnumbering episodes per game in rounds 21-100;
  we had 2.1 to 2.5. Their kills came mostly from those.
- **Rounds 151-300.** We died 1.79 times per game, the top 5 0.61. Of our deaths there, 85% were to champions, 53%
  with no ally within 6, 51% outnumbered and 76% on our own half.
- **Togetherness.** Top-10 champions had 2 or more allies within 10 tiles 60% of the time; ours 48%. Their opening
  captures had 3 or more champions together 44% of the time; ours 21%.
- **Contacts.** Top-10 contacts started paired 67% of the time; ours 45%. Rounds with two of their champions hitting
  the same foe: 25% vs our 15%.
- **Reinforcement.** It was about zero for both teams in the 3 rounds after contact. **Superiority is decided before
  contact, not during it.**

### 6.4 The economic consequence

v63 against the top 10, 65 games (18 October), per game, us / them:

| Measure | Us | Them |
| --- | ---: | ---: |
| Banked gems at round 100 | 89 | 68 |
| Banked gems at round 300 | 317 | 392 |
| Banked gems at round 500 | 524 | 787 |
| Share of champion-rounds dead | 17.5% | 4.9% |
| Gold earned | 3,057 | 4,972 |
| Gold from kills | about 90 | about 390 |
| Captures | 26 | 35 |
| Gems lost on death | 89 | 53 |

We led early. Their income rose after round 200 and ours stayed at about 1.1 gems per round. Among alive rounds the
split of time between farming and walking was the same. The macro gap was mostly the cost of our deaths.

The farm gap that remained was **which** camps we took, not how fast. Captures per game were similar, but the top 10
took 12.3 gems per capture to our 8.5 (23 October): we took 4.5 more tiny captures and half as many 40-plus-gem
groups. The rich two-elk groups needed 3 or 4 champions together, which brings us back to formation.

### 6.5 What was not the cause

We spent days on each of these before ruling it out:

- **Spells.** The 14 October spell gap had closed by 18 October.
- **Damage concentration.** Both teams put about 97% of hits on the top target.
- **Shop.** In 375 games on patch 2.0.0 the top 5 used none of the new item families. They bought 1.5 to 2 times
  more after round 150 because they earned more. Copying their build lost locally.
- **Draft.** A study of 3,160 top-team games (by another team) found every champion within ±0.5 points once team
  strength is subtracted. Our own draft-v1 copy lost online, 10 changed games for and 24 against.
- **Activity mix.** Time camping, fighting, walking and idle was the same as our rank band's.

---

## 7. What worked

| Change | When | What it did | Measured result |
| --- | --- | --- | --- |
| goldval (v96) | 21 Oct | Stop chasing gold-only camps before round 940 | Our deaths per game 9.9 → 7.5 (143 pairs); +16 online |
| horfocus (v98) | 21 Oct | Focus build for Heart of Ruin, as the top 10 did | Deaths in losses 11.0 → 6.7; +12 online |
| stallfix (V13) | 22 Oct | Remove stuck and idle champions | +11 online |
| bank-v1b (v65) | 18 Oct | Do not switch altars halfway through a banking trip | Elkring switches 16 → 0 per game; changed games 17 for, 4 against |
| recall escape (v72) | 19 Oct | Recall out of losing fights | Promoted by the two-step judge |
| team fight (v76) | 19 Oct | Finishing layer: hit the lowest rival under 50% when safe | Against ranks 31-55: kills +1.33, deaths −1.43 per game |
| P_MONO | 16 Oct | Fix 0 gems on the contest map (the bot skipped monoliths) | Online 1-43 before the fix |
| Fuel fixes | 13, 17, 25 Oct | Turns cut by overruns (start-up work, wards reading every group, lanes) | Lanes stopped collapsing |
| kvvl deterministic fuel | 24 Oct | Decisions stop depending on fuel left | A 20-instruction probe stopped changing 248 of 312 local games |
| v21 | 29-30 Oct | t10plan-v17 + Heart of Ruin self-shield whenever ready | 400 games against ranks 5-20: 47 changed, 34 for, 13 against, +21 with a bar of 13.7. Without its flee rules (v30): −6 |

**What they have in common.** Each fixed something broken or removed a clear source of deaths. Each mechanism was
large enough to move a full-game result. None of them was a clever new fight rule.

---

## 8. What did not work: the candidate ledger

The main lines we closed. "Local" means a local judge; "online" means paired online games.

### Fights and deaths

| Line | Dates | Idea | Outcome |
| --- | --- | --- | --- |
| P_HOLD, caster ball, group fight, volley | 14 Oct | Copy top-team fight shapes as switches | Won locally, lost online (P_HOLD 0-7) |
| defense-v1/v2 (DH1-5) | 18 Oct | Defend our half as one module | Local 34% then 55%; online 14% vs 25%: rejected |
| micro MI1 to MI3 | 18 Oct | Finish low foes; recall to escape; hit whoever dies soonest | MI2 made low-hp deaths worse (22% → 27%); MI1 was parked after 3 versions with no gain; MI3's situation was too rare locally to judge |
| foe-v1/v2 | 18 Oct | No camp hits with a rival within 4 | Passed locally; tied online (37 for, 39 against) |
| kill-v1/v2 | 18 Oct | Hunt killable rivals | Finishable rivals killed within 5 rounds 40% → 58% locally, but failed on fuel; rejected online |
| getout, escape, duel-v1 | 19 Oct | Leave fights when behind | Under the bar; duel-v1's expected gain was −0.3 deaths per game |
| shop-parity (v77) | 19 Oct | Match rivals' hp share in the shop | Rejected online: max hp is a correlate, not a cause |
| homedef-v1 (v100) | 21 Oct | A lone champion falls back to an ally when invaded | Rejected (29 up, 46 down); own-half death share unchanged |
| powerv-v1/v2 | 21 Oct | Walk out below 35-45% local hp share | Local −10 and −38 |
| pairs line (pw3, mgwp, join) | 24 Oct | Walk and wait with an ally | Alone share −2 to −3 points online, every time; 0 wins |
| pelea-v1 | 24-25 Oct | Enter fights only with numbers | Not above the bar |
| superiority u7 | 27 Oct | Flee toward an ally when outnumbered | Online +5 with a bar of 10.4; replays showed the retreat changed nothing (died within 10 rounds 18% vs 19%) |
| t10plan-v22 to v31 | 29-30 Oct | Heart of Ruin dash, reset shot, earlier verdict, wider shield, durability emblem, Varg instead of Heart of Ruin | 6 to 11 of 80 against v21's 12; none passed |

### Farm, macro and draft

| Line | Dates | Idea | Outcome |
| --- | --- | --- | --- |
| draft-v1 (v67) | 18 Oct | Top-30 draft by team size | Online 10 for, 24 against |
| finish-v1 to v3 | 18 Oct | Endgame race planner | Failed on fuel three times; closed |
| caprecall-v1 (v70) | 18 Oct | Capture and recall on the same tile like the top 10 | 16-16 on changed games |
| value-v1, need2, elksplit | 22 Oct | Value-based target choice | Passed locally (+30 on 720 pairs); small online |
| opening-near | 24 Oct | Open on near camps like the top 10 | Local state at round 300 worse |
| o101-o107 farm pricing | 25-27 Oct | Price camps by outnumbering, strong groups, late gold | Every one lost online or on the bench |
| t10plan schedule (v2-v4q) | 27-28 Oct | Copy the top-10 camp schedule per map and round | Online −8 to +2; the schedule cost 40-44% of gold captures |

### Learning approaches (16 October)

| Line | Idea | Outcome |
| --- | --- | --- |
| Genetic islands | 22 fight parameters, then 48 macro genes, on 8 islands | The 14:15 "champion" was level with v44 on 100 fresh maps: selection luck. One genome (b672) held 34-10 locally but never beat the online bot |
| DQN | 25-32-7 Q-network on the fight decision hook | Noise; both ideas rejected |
| Imitation | Clone the #1 team's retreat curve | Died 89 times vs 34 against caster bots; the paired version was neutral online |
| RL assessment | Full-policy RL | Not viable: no step simulator, about 6 local games a second, and a fuel budget that fits only a 2-5k-multiply network |

**Count.** From 18 October to 30 October we ran something like 60 to 80 online candidates. Fewer than 10 passed.

---

## 9. Why our measurements failed us

This is the most important section. With a sound judge, a team can recover from bad ideas. We had bad ideas **and**
a judge that could not tell them apart.

1. **Local self-play lied about fights.**
   - On 16 October, 0 of 8 fight rules that won locally won clearly online.
   - A real 55% change passed our 260-map local gate only 12% of the time. Threads added maps until one passed.
   - Our local rivals were our own old bots. They never invaded in packs, never punished a walk to the altar, and
     never contested the middle. kvvl's J2 local judge said +10.4; online said +4.
   - Even the "hard panel" overrated small pieces: pw3 was +6 locally and −1 online.
2. **Fuel chaos.** Any recompile changed real fuel use from the first turn. Decisions that checked `fuel_ok()` then
   flipped from round 2 or 3, and about one game in four came out different for reasons that had nothing to do with
   the change. Two builds with the same decisions gave 35 different results in 145 games. Until the deterministic
   meter of 24 October, every A/B test, local and online, carried this noise.
3. **Online power was low.**
   - A batch had about 27 to 38 changed games.
   - With the 18 October rule, a neutral change passed 2.2% of the time, a +5-point change 22%, a +8-point change
     50% and a +10-point change 70%.
   - A +3% change needed about 10 batches to pass, a +5% change about 4.
   - Most of our pieces were worth +1 to +3%: vco +14 in 500 games, monoguard +6 in 250, kvvl +4.
4. **Rival drift.** Top bots changed every few hours; the same pairing and map differed 70 to 84% of the time after
   30 minutes. A week-old benchmark was a different opponent.
5. **Data bugs.**
   - 22% of our online game records were byte-identical rematches. Until we deduplicated them, they inflated sample
     sizes.
   - 4.8% of rows had flipped side and result.
   - The old replay decoder had camp positions and rewards wrong on 18 maps.
   - The 27 October "jackpot" finding (1,018 gems in rounds 151-300) came from summing a group's reward over each of
     its camps; the engine pays it once. Two candidate lines were built on it.
6. **Measuring the wrong unit.** For a week we counted wins on changed games. The state model built on 24 October
   (gold, deaths, monster damage and margin at round 300-400) had half the error. Exposure tracing (how often a rule
   actually changes a decision) came on 23 October. It showed some pieces changed 1% of decisions and could never be
   measured.

**What a sound judge would have looked like from day 3:**
- deterministic fuel;
- pinned online groups against current strong rivals;
- a pre-declared sample size;
- paired state metrics at round 300 as well as wins;
- a firing counter for every new rule.

We had all of these by 25 October. We needed them by 15 October.

---

## 10. Process mistakes

1. **Five methods in three weeks.** Switches (13-15 October), learning (16 October), the teammate base
   (16-17 October), the from-scratch lab (17-18 October), the online loop (18-27 October) and copying the top-10 plan
   (27-30 October). Each switch was a reaction to a bad day, not to evidence that the method was wrong.
2. **Too many parallel fronts.** On 16 October: 7 genetic islands, a DQN, imitation and three fix threads. On
   24 October, a 16-slot online day with 7 repeats. Threads stepped on each other's base versions. The online bot was
   once not the bot the local gate compared against (16 October).
3. **Symptoms instead of the system.** On 19 October the user asked for exactly the right thing: "the whole system is
   flawed, we have to pinpoint the main issue", and no single-rule patches. We still produced single-rule
   candidates for another ten days, because each thread owned one rule and the loop rewarded one rule per batch.
4. **Ignored interactions.** The 23 October audit found the code did what each candidate claimed in 7 of 7 cases. The
   failures were known interactions nobody checked:
   - a shooting rule that rooted Vesper every round she shot;
   - a fuel guard that froze a champion for 800 rounds;
   - early gold spent on gems instead of power.
5. **Operations held together by notes, not code.**
   - The online loop died with its container.
   - Status reports were missed for 34 to 61 minutes at a time.
   - Uploads were duplicated, and an online quota hour was lost.
   - The shared folder filled up and writes were silently dropped.
6. **Late study of the top.** Our first deep top-team study was on 15 October, but the decisive measurements
   (formation, outnumbering rates, pairing at contact) came between 18 and 24 October. The top-10 benchmark on current
   bots arrived on 23 October.

---

## 11. Comparison with the top and with our peers

| Measure (source) | Top 5 or top 10 | Us |
| --- | --- | --- |
| Deaths per game, rounds 151-300 (top 5, 27 Oct) | 0.61 | 1.79 |
| Champion below 45% hp dies (677 fights, 18 Oct) | 11% | 48% |
| Time with 2+ allies within 10 tiles (top 10, 27 Oct) | 60% | 48% |
| Opening captures with 3+ together, rounds 1-50 | 44% | 21% |
| Contacts that start paired (24 Oct) | 67% | 45% |
| Gems per capture (23 Oct) | 12.3 | 8.5 |
| Strong two-elk groups per game (vs ranks 56-70) | 0.7, with 3-4 champions, no deaths | 0.3, with 2-3 |
| Heart of Ruin shield per game (v16 online) | 16.9k | 5.2k |
| Heart of Ruin kills / deaths per game | 2.67 / 0.81 | 0.68 / 4.0 |
| Gold per game against ranks 5-20 (v17) | 6,919 | 3,537 |
| Damage in even fights | equal | equal |

**Peers.** [EvilMangohh](https://github.com/toyeshhm/cambridge-battlecode-2026) peaked at rank 22 before the patch
and was 107th on 8 November, just above us. They won 4 of 100 against the current top 10, close to our 7 of 80
against ranks 5-20. They worked much like us, with parallel agents, switches and a judge agent, and reached the same
conclusions:
- local A/B tests against your own bots lie;
- merging seven changes hid the four that hurt;
- wasted turns and replay bugs mattered more than fight logic;
- every "play safer" rule cost kills.

They did not close the gap either. Two teams with this much tooling stalling at the same level is evidence that the
missing piece was not tooling but **team-level positioning designed in from the start**.

---

## 12. Lessons, and the plan we would follow next time

### Lessons

1. **Build the judge before the bot.** Deterministic fuel accounting from the first line of code. A pinned online
   benchmark against the current top 10, refreshed every few days. Paired game-by-game comparison with a
   pre-declared sample size.
2. **Local tests only check that nothing broke.** Never use them to decide whether an idea is good, least of all for
   fights.
3. **Find the one number that separates winners from losers, then design for it.** For this game it was being
   outnumbered at contact. A team plan from the draft (squads, roles, routes, rally points) was needed, not a rule
   that fires once enemies are near.
4. **First stop dying from bugs.** Stalls, recall loops, oscillation, fuel overruns, wrong altars. That was +200
   rating for us in two days.
5. **Size every candidate before testing it.** Write down how many decisions per game it changes, the expected effect
   in deaths or gold, and the interactions it touches. If the expected effect is under the judge's resolution, bundle
   it or drop it.
6. **One base, one method, one owner per file.** Change methods only on evidence, and on the same base.
7. **Check every analysis number against the engine** before building on it.
8. **No machine learning without the game budget it needs.** At most, CMA-ES on a few dozen constants of a rule bot.
9. **Automate operations.** Loop liveness, quota use, upload checks and disk alerts belong in code, not in notes.

### A four-week plan, knowing what we know now

| Week | Goal | Exit check |
| --- | --- | --- |
| 1 | Rules in our own words, trusted engine and upload path, deterministic fuel meter, replay decoder validated against the engine, online pinned benchmark against the top 10 | A null change scores 0 changed games; decoder totals match the engine on every map |
| 1-2 | Simple bot: economy, banking, recall, no bugs; one-capturer rule; stalls and fuel fixed | Beats the starter bots everywhere; zero stuck champions in 100 replays |
| 2 | Study the top 10's formation, routes and contacts from replays, and write the team plan as data | A one-page design with expected numbers (allies within 4, contacts paired) |
| 2-3 | Implement the team plan as one module from the draft: squads, routes, rally, engage rules | Online: contacts paired from 45% toward 65%; deaths in rounds 151-300 halve |
| 3-4 | Large candidates only, stacked and sized; refresh the benchmark every 3 days | Each candidate moves its metric and passes the paired online judge |
| 4 | Freeze 3 days before the deadline; only bug fixes | The upload is the tested zip (hash checked) |

---

## 13. Open questions

To check against the finalists' replays and writeups after 18 November:

- How do they keep 2+ allies near without losing farm throughput? By routes planned at the draft, or by local rules?
- Do they decide engagements by local numbers at contact, or by a team-level plan of where the fight happens?
- How do they take two-elk groups with 3-4 champions and no deaths? Shield timing, pull order, or positioning?
- Did any of them use learning, and with what game budget?
