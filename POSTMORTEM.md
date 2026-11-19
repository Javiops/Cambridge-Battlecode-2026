# Live Love Larp: Cambridge Battlecode 2026 postmortem

**Peak ladder rank #25** (14 October, about 370 teams on the board, top 7%). **Peak rating 2,019.**
**87th international** at the close, 125th of 826 teams overall (top 15%). Final bot: v21, site version **212**.

We did not make the finals. This is the write-up of how a small team, working almost entirely through AI coding
agents, climbed from a bot that lost 0-5 on day one to the top 7% of the ladder, what we found that most teams never
measured, and the one design mistake we could see clearly and still never fixed.

Every number here comes from our own logs, online match groups and replay decodes. Where something is an estimate,
it says so.

| Season at a glance | |
| --- | --- |
| Ladder peak | **#25** on 14 October (site version 29), **#33** on 15 October, **#52** on 24 October after the field doubled |
| Rating | 1500 → **2,019** peak, including **+207 in two days** (21-23 October) |
| Final standing | 125th of 826 overall, 87th international (8 November ladder) |
| Uploads | 212 site versions in 3 weeks |
| Online testing | ~150 games per hour of paired challenges from 15 October; 60-80 candidates judged online, fewer than 10 passed |
| Final bot | 8,859 lines of C++20, 249 `P_*` switches, one header per champion |
| Team | One main developer driving ~80 parallel Claude Code threads, a Windows PC for local arenas, one teammate's bot as our mid-season base |

---

## TL;DR: what every future team should take from this

1. **The engine is deterministic. Your bot probably isn't.** If any decision reads `fuel_remaining()`, a recompile
   with no logic change reshuffles about a quarter of your games. A 20-instruction probe changed 248 of 312 of our
   local games. We fixed it with a deterministic fuel meter and got that to 1 in 52. Do this on day one, or every
   A/B test you run is noise.
2. **Games are lost before the first hit.** In equal fights we dealt the same damage as the top 10. We lost because
   our champions arrived alone. Top-10 contacts started paired 67% of the time, ours 45%. Superiority is decided
   before contact, not during it.
3. **Share facts, not orders.** With 8 bytes of team memory, we wrote orders into each other's bytes; 231 of 278
   were dropped because the receiver knew things the sender didn't. HBH, who reached the international round of 32,
   shared sightings and let each champion keep deciding. That is the difference in one sentence.
4. **Local self-play lies about fights.** 0 of 8 fight rules that won locally won online. Judge on paired games
   against real, current opponents.
5. **The fastest rating gains are bug fixes.** Our only big jump, +207 in two days, came from removing stalls, a
   gold-chasing habit and a bad build, not from a clever new idea.

---

## 1. The game, briefly

Two teams draft 3 to 5 champions. Champions farm neutral camps (wolves, elk, gem and gold clusters, golems, 20,000 hp
monoliths), then carry gems to an altar and channel a tribute of ceil(bag/10) turns. First to bank 1,000 gems wins. A
champion who dies drops the whole bag to the killer, who also gets 100 gold, and sits out 60 rounds.

The constraints that shaped everything:

- **No shared brain.** Every champion runs its own copy of the bot with its own vision. The whole team shares
  **8 bytes** for the entire game, plus 1,024 bytes written during the draft.
- **Fuel.** 100,000 units per turn, roughly one per WASM instruction (a trivial loop iteration costs about 9, one
  `printf` about 570). An overrun suspends the bot mid-code until next round.
- **Determinism.** The same two bots on the same map and sides play the identical game, byte for byte.
- **Patches.** Three balance patches in week 2, then patch 2.0.0 on 25-26 October rebalanced every champion, cut the
  camp economy and grew the map pool from 35 to 70.

---

## 2. The final bot: v21 (site version 212)

Source: `bots/live-love-larp/src/`, the unchanged code of the zip that went live on 30 October.

| Part | What it does |
| --- | --- |
| Draft | Reads the map in the draft turn. Default roster Heart of Ruin, Vesper, Marcella, Ryth, Vendetta (the top-10 picks of 22 October); on far maps (spawn-to-altar path 60+) Heart of Ruin is swapped out |
| Farming | Camp groups claimed through shared memory. One champion captures and the rest move on, since a capture splits between everyone on the reward tiles |
| `plan_t10.h` | Per-map, per-50-round table of which camp groups top-10 **winners** spent time on, built from about 600 top-10 vs top-10 games. Multiplies our target scores from round 150 to 650 |
| Roles | On near maps, escorts follow the carry: Heart of Ruin with Vesper, Ryth with Marcella |
| Fights | First-contact verdict from a two-sided damage model, focus fire on one target, caster kiting, flee rules when outnumbered |
| Heart of Ruin | v21's own change: self-shield whenever ready in combat. We had measured our shield output at 5.2k per game against the top's 16.9k |
| Banking | Altar choice that never switches mid-walk |
| Fuel | Deterministic meter (`fuel_okc`): heavy passes are charged a fixed price, so a change in one place cannot flip decisions elsewhere |

**How it got in.** v21 was judged on 400 pinned online games against ladder ranks 5 to 20. 47 games changed result:
34 in its favour, 13 against, **+21 against a pre-set bar of 13.7**. The same build without its flee rules scored
−6, so the flee rules were carrying real weight.

**Lineage.** v3 (13 Oct) → study22-28 → v44 genetic fight parameters → teammate base **v53** → bank-v1b, recall escape,
team fight → goldval, horfocus, stallfix → V20 (one header per champion) → **kvvl** (deterministic fuel) → e1foco →
t10plan-v2 to v21 → **v21**.

---

## 3. The climb

| Date | Rating | What happened |
| --- | ---: | --- |
| 13 Oct | 1500 | First upload. Lost 0-5. 24% against the top 10 by evening |
| 14 Oct | | **#25 on the ladder** with site version 29, after a day of studying top-10 replays and coding their habits as switches |
| 15 Oct | 1618 | #33; top-2 dissection over 101 games; online test loop goes live |
| 16 Oct | 1669 | Genetic fight parameters (v44), then the teammate's bot becomes our base |
| 18 Oct | 1728 | v53 base; paired online games become the main judge |
| 21 Oct | 1649 | Low point: a week of single-rule fight patches |
| **22-23 Oct** | **1846** | **goldval + horfocus + stallfix: +207 in two days** |
| 24 Oct | 1862 | #52 on a ladder twice the size; deterministic fuel meter lands |
| 26 Oct | 1875 | Patch 2.0.0 reshuffles everything |
| 30 Oct | 1876 | v21 goes live as site version 212 |
| 4 Nov | 1908 | International qualifier (top 8 international teams advance) |
| 8 Nov | 1925 | Ladder still open after the qualifier |

The +207 is worth dwelling on, because it came from three changes that were all, in effect, bug fixes:

| Change | What it fixed | Measured |
| --- | --- | --- |
| goldval (v96) | Champions chased gold-only camps before round 940 and died on the way | Deaths per game 9.9 → 7.5 over 143 pairs; +16 online |
| horfocus (v98) | Heart of Ruin bought a generic build instead of the focus build the top 10 used | Deaths in losses 11.0 → 6.7; +12 online |
| stallfix (V13) | Stuck and idle champions (one froze for 800 rounds behind a fuel guard) | +11 online |

Earlier fixes in the same spirit: **P_MONO** (our bot ignored monoliths and scored 0 gems on `contest`, 1-43 online
before a 19-line fix), **bank-v1b** (altar switches on `elkring` went from 16 per game to 0), and fuel fixes that
stopped `lanes` collapsing from 43 lost turns per game.

---

## 4. Finding 1: the deterministic engine and the non-deterministic bot

This is the result we are proudest of, and the one we found too late.

**The symptom.** Our online judge could not tell a +5% change from noise. Two builds that made the same decisions gave
different results in 35 of 145 games. Paired games diverged at a median of round 3.

**The cause.** The engine is fully deterministic: we confirmed 60 duplicated online pairings played identical
games. But our bot, like most, checked `fuel_ok()` before expensive work. Any recompile shifts real fuel use from
turn 1. A branch that read "skip the path search, fuel is low" flips on round 2 or 3, and from there the whole game is
different. In our measurements:

- adding a 20-instruction probe that does nothing changed **248 of 312** local games and 43 results;
- adding one `printf` in init shifted a champion's first turn and changed about **27%** of games;
- HBH independently measured the same effect at **36-38%** of results flipped by a no-op rebuild.

**The fix: a deterministic fuel meter.** Decisions stop reading real fuel. Instead every section of the turn charges a
fixed, pre-measured price to a virtual meter: path search 15k, target choice 28k, engage logic 19k, chase 17k, altar
routing 17k, and so on, scaled by how many foes are within 10 tiles. The turn quota is 88,000 virtual units; real fuel
only vetoes work below an emergency floor of 9,000.

| Meter version | Games changed by the 20-instruction probe |
| --- | ---: |
| No meter (kvvl) | 248 / 312 (79%) |
| v1, flat prices | 225 / 312 |
| v2 | 30 / 52 |
| v3, foe-driven prices | 6 / 52 |
| **v4** | **1 / 52** |

With it, we could replay a candidate alone on the exact online groups the base had already played, and every changed
game was caused by the candidate. HBH dealt with the same chaos by playing far more games (about 31,000); we removed
it at the source instead.

**Lesson.** Before writing a single strategy rule, make a no-op rebuild produce zero changed games. Put the test in CI.

---

## 5. Finding 2: we lost the fight before it started

Every study, with every base, against every rank band, told the same story.

**We did not fight worse in even fights.** Over 677 fights against the top 10 we dealt the same damage and brought them
low as often as they brought us low. Damage per contact round was equal. Both teams put about 97% of hits on the top
target. The spell gap we saw on 14 October was closed by the 18th.

**We died far more.** Death census against the top 10, 67 games, deaths per game:

| Situation | Us | Them |
| --- | ---: | ---: |
| Running away | 2.57 | 0.63 |
| Channelling a recall or tribute | 1.42 | 0.22 |
| Walking | 1.30 | 0.54 |
| Fighting, not outnumbered | 1.21 | 0.34 |
| Hitting a camp | 0.84 | 0.10 |
| **Total** | **8.78** | **2.69** |

A champion of ours below 45% hp died **48%** of the time; one of theirs **11%**.

**The root: who arrives with more champions.**

| Measure | Top 10 / top 5 | Us |
| --- | ---: | ---: |
| Contacts that start paired | 67% | 45% |
| Time with 2+ allies within 10 tiles | 60% | 48% |
| Opening captures with 3+ champions together | 44% | 21% |
| Outnumbering episodes per game, rounds 21-100 | 4.0-4.9 | 2.1-2.5 |
| Deaths per game, rounds 151-300 | 0.61 | 1.79 |
| Reinforcements in the 3 rounds after contact | ~0 | ~0 |

That last row is the key. Nobody wins by calling for help once the fight starts. The team that is already there wins.
Of our deaths in rounds 151-300, 53% had no ally within 6 tiles and 76% were on our own half.

**What it cost.** Against the top 10 we led banked gems at round 100 (89 vs 68). By round 500 it was 524 vs 787. Our
champions spent 17.5% of their rounds dead, theirs 4.9%. Against ranks 5-20 with v17, they earned 6,919 gold per game
to our 3,537. Most of the economic gap was the price of our deaths, not slower farming.

---

## 6. Finding 3: coordination in 8 bytes, orders vs facts

If the problem is arriving together, the 8 shared bytes are where the fix should live. We tried hard. It is the part
of the season we would do most differently.

**What v21 shipped with:**

| Bytes | Use |
| --- | --- |
| 0-3 | Camp claims, 6 bits per champion, with no round stamp |
| 4 | Focus target |
| 5-6 | One respawn slot, last writer wins, two meanings |
| 7 | Danger at an altar, held 45 rounds |

**What we tried and how it failed:**

- **orch (v2 to v14): a free champion writes an order into a teammate's byte.** The receiver accepted it at turn
  start, then re-checked it against its own state. If its travel estimate was stale it dropped the group; if it
  arrived at a camp still respawning it dropped it again. On `elk_arena`, **231 of 278 orders were dropped**, and the
  planner dropped its own group 266 times out of 280.
- **t10plan v9 to v11c: squads, follow-the-leader, walk in a block.** Champions spent 10 to 25 rounds without
  hitting anything while they waited for each other. Results: 6 to 47 of 140.
- **Pair rules (pw3, mgwp, join): walk and wait with an ally.** The "alone" share fell 2 to 3 points online every
  single time, and wins never moved.
- **Our teammate's Alerts V2: shared enemy sightings in bytes 4 and 7.** This was the right idea. It shipped as v59
  **bundled** with wards and a banking switch that broke `lanes`, went 24-116, and was never tested alone. We threw it
  out with the rest of the bundle.

**What HBH did instead** (from their write-up; they published no code). Each champion publishes "I see an enemy here"
in the low bits of its own turn-priority integer, a slot only it writes, which does not even spend the 8 bytes. Every
champion then runs its normal logic with a wider view: engage only if the nearest enemy is within 4 tiles, a depth-3
team search, camp pricing. Rules constrain that logic but never replace it. If a sighting is stale or missing, the
champion decides exactly as it would without it.

In one line: theirs was *know more, decide the same*; ours was *do what someone else says, with data they no longer
have*. And they tested each piece alone on held-out maps with the bar written down before looking.

---

## 7. Finding 4: copying the top 10, and what actually transferred

On 22-28 October we decoded about 600 top-10 vs top-10 games plus our own, with a replay decoder we validated
against the engine. Some of what we learned:

- Top-10 winners concentrated their gems: Vesper took 28% and Marcella 30% of the team's gems, about 2,000 gold each,
  with 0.7 deaths. Our champions were flat at 17-26% each with 2.3-2.9 deaths.
- The top 10 took **12.3 gems per capture** to our 8.5. We made 4.5 more tiny captures per game and half as many
  40+ gem groups. The rich two-elk groups needed 3-4 champions together: formation again.
- Their Heart of Ruin: 2.67 kills and 0.81 deaths per game. Ours: 0.68 and 4.0.
- Shop: on patch 2.0.0 the top 5 used none of the new item families. They simply bought more after round 150,
  because they earned more. Copying their build lost locally.
- Draft: once team strength was subtracted, every champion was within ±0.5 points. The draft was not the lever.

**What transferred.** Copying the top-10 camp *schedule* outright cost us 40-44% of our gold captures (online −8 to
−11). What worked was using it as a soft multiplier on our own target scores, winners only, from round 150, never
cutting gold-only camps. Stacked with the Heart of Ruin self-shield, that became v21.

---

## 8. The graveyard

From 18 to 30 October we judged 60 to 80 candidates online. Fewer than 10 passed. A selection:

| Line | Idea | Outcome |
| --- | --- | --- |
| P_HOLD, caster ball, volley | Copy top-team fight shapes | Won locally; P_HOLD 0-7 online |
| defense-v1/v2 | Defend our half as one module | Online 14% vs 25%: rejected |
| kill-v1/v2 | Hunt killable rivals | Kills within 5 rounds 40% → 58% locally; failed on fuel, rejected online |
| draft-v1 | Top-30 draft by team size | 10 changed games for, 24 against |
| homedef-v1 | Lone champion falls back to an ally when invaded | 29 up, 46 down |
| superiority u7 | Flee toward an ally when outnumbered | +5 against a bar of 10.4; replays showed nothing changed (18% vs 19% died within 10 rounds) |
| Genetic islands | 22 fight genes, then 48 macro genes, 8 islands | The "champion" was selection luck: level with v44 on 100 fresh maps |
| DQN | 25-32-7 Q-network on the fight hook | Noise |
| Imitation | Clone the #1 team's retreat curve | Died 89 times vs 34 against caster bots |
| From-scratch lab | New layered bot following a published top player's method | Ranked 27th of 28 against our own old bots |

What the winners have in common: each fixed something broken or removed a clear source of deaths, and each was
large enough to move a full game. None was a clever new fight rule.

---

## 9. Why our measurements lied, and what a good judge looks like

1. **Local self-play.** Our local rivals were our own old bots. They never invaded in packs or punished a lone walk to
   the altar. 0 of 8 locally winning fight rules won online. A real 55% change passed our 260-map local gate only 12%
   of the time.
2. **Fuel chaos** (section 4), until 24 October.
3. **Low power.** A batch had 27-38 changed games. A +5-point change passed our first online rule 22% of the time.
   Most of our pieces were worth +1 to +3%, invisible to a single batch.
4. **Rival drift.** Top bots changed every few hours; the same pairing and map differed 70-84% of the time after
   30 minutes.
5. **Data bugs.** 22% of online records were byte-identical rematches until deduplicated; 4.8% had side and result
   flipped; an old replay decoder had camps wrong on 18 maps; one "jackpot" finding came from summing a group reward
   over each camp when the engine pays it once.

**The judge we had by 25 October, and should have had by 15 October:** deterministic fuel; the candidate replayed
alone on the base's pinned online groups against the teams just above us (later ranks 5-20); a pass bar of
(for − against) ≥ 2·√(changed games) declared before reading; state metrics at round 300 (gold, deaths, margin) as
well as wins; and a firing counter printed for every new rule, so we knew how often it actually changed a decision.

---

## 10. Process mistakes

- **Five methods in three weeks:** switches, machine learning, the teammate base, a from-scratch lab, the online loop,
  then copying the top 10. Each switch was a reaction to a bad day, not to evidence.
- **Too many fronts.** On 16 October we ran 7 genetic islands, a DQN, imitation learning and three fix threads at once.
  Threads stepped on each other's base versions.
- **Symptoms instead of the system.** On 19 October we wrote down exactly the right instruction to ourselves: "the
  whole system is flawed, find the main issue, no single-rule patches". We kept shipping single-rule candidates for
  ten more days, because every thread owned one rule.
- **Bundling.** The teammate's sightings died inside a bundle. Test pieces alone.

---

## 11. Advice for next year's teams

1. **Day 1:** deterministic fuel accounting, a replay decoder checked against the engine, and a no-op rebuild that
   changes zero games.
2. **Day 2:** a pinned online benchmark against the current top teams, paired by map and side, with the pass bar
   written before you look.
3. **Week 1:** remove every stall, loop, overrun and wrong altar. It is the cheapest rating you will ever get.
4. **Week 2:** measure formation at contact (allies within 4-6 when the first hit lands). If you are below the top,
   that is your problem, not micro.
5. **Use the shared memory for facts** (sightings, claims with a round stamp, a muster point), never for orders.
6. **Test every piece alone.** A good idea bundled with a bad one is a dead idea.
7. **Freeze three days early.** Upload the exact zip you tested and check its hash.

---

## About the ranking numbers

The ladder peak of #25 and #33 come from our ladder checks on 14 and 15 October, when about 370 teams were rated;
the board grew to 826 by the end. #52 is the best rank we recorded after it grew (24 October). The peak rating of
2,019 is the highest on our team's rating history on the competition site; our own snapshots, taken less often,
topped out at 1925. The final placement that
counted was 87th among international teams, and the top 8 international teams advanced.

*Thanks to HBH, DOOMSDAY and EvilMangohh for publishing their write-ups; reading them side by side with our own data
is what made sections 4 and 6 possible.*
