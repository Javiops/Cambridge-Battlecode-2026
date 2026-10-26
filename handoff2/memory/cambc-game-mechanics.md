---
name: cambc-game-mechanics
description: Measured CAMBC engine facts that are not in the rules text (monster focus-fire, capture split, ally visibility, turn order) and what they imply for the bot
metadata:
  type: project
  modified: 2026-10-16T19:29:00.000Z
---

Measured from replays 2026-10-13 (decoder: /mnt/project-files/arena/tools/replaydump.js):

- **Monsters focus one champion: the first that damaged the group**, not the nearest (top-2 replay
  study 2026-10-15: first hitter is the target in 84% of Mite's and 89% of Univardisty's engagements,
  n=296/267, analysis/top2-dissection-2026-10-15/targeting_spells.md; the rest likely the hitter
  leaving range 3; ties and target death unmeasured). All wolves of a 3-wolf group hit that one body
  (60 damage/round), so the tank should hit first and ranged open from 3 tiles a turn later; the tank
  takes the whole group's strength: fight lasts hp/(dps*n) rounds.
- **Only champions standing on the group's spawn tiles share the capture reward** (rules:
  "allies on the region split the reward"). Top teams let ONE champion capture and carry
  ~66 gems to the altar while the others move on; our v4 does the same (`i_capture`).
- **Allies out of vision throw api_not_in_vision** for position()/health(); only
  `bc::champions(ally)[i].is_alive()` works everywhere. Use `bc::vision::champions(ally)`
  for positions; match handles with `==` for the ally index.
- **Turn order inside a team is draft order** (lowest index first), so the first pick
  claims targets first. Draft strong bodies first (Vendetta, Varg), Cassi & Issac
  third: with Cassi at index 0 the weakest body took the best jobs.
- **Cassi & Issac** are two bodies with separate bot instances that die together; v4 makes
  Cassi follow Issac's target and never claim on her own.
- **Engine 1.0.3 (10-23 probe): a ranged STEP also removes the attack (can_attack 0), and a ranged hit removes the step (145/145 Vesper). Abilities (dash) still work after a hit: top-10 Vesper shoots then dashes.**
- **A ranged champion that attacks cannot move that turn** (probe 2026-10-13: Cassi
  can_move()=0 after 64 of 64 hits; melee keep can_move). So "hit first, then step" is
  melee-only; ranged step first, then shoot (fight.h hit_now enforces this).
- **Shared memory is 8 bytes** (shared_memory.size()==8). Bytes 0-4 claims, 5-6 BC group,
  7 = help call (foe idx+1 low 3 bits, round&31 high). Writes past 7 fail silently.
  Each champion's program keeps its own globals/statics between turns (private memory, separate
  from the 8 shared bytes); survival across death/respawn inferred from "dead champions still get
  turns", not tested (thread "How camps pick their target", 2026-10-16 19:29).
- v3's individual farming reaches 1000 gems by round 500-650 on 7 of 9 official maps;
  only rows (3-wolf groups) needs pack farming. Packing up on easy maps slowed farming
  a lot (see [[cambc-bot-project]]).

**Why:** each fact cost hours of arena iterations.
**How to apply:** keep squad/capture logic consistent; verify with
`arena/tools/captures.py GAMEDIR` (capture events per team) and `gamesum.py OUTDIR`.

**Spells (probe 2026-10-14, P_CDPROBE in fbase):** enemy `abilities()[k].cooldown()` and `.info()` are readable for visible
enemies. Damage = modifier x focus. Stellar: damage 2.0x (exclusive) + ground AoE 1.4x radius 1 (exclusive); Tavi: attack reset + stun 1 round with 2.2x damage (exclusive); Cassi: damage 2.0x (exclusive) + pure
1-round stun (free); Issac: attack reset + dash. All range 4, cooldown 8. "Exclusive" = exclusive_with_movement: cannot
be cast after a step that round, so a caster walking into range cannot answer that round; the stander shoots first.
Late game foci reach Tavi 450 (990 per stun) and their ready volley near us 1000-1800.

**Fuel (2026-10-14):** one `bc::distance_field` BFS ~8k on rows/corners-size maps. `d.get(p)`/`vis.is_set(p)`
~55 each: copy once (`d.export_linear_buffer(buf)`, read `buf[y*width+x]`). One `std::cout` line per camp
group exhausted fuel on corners, lanes, expanse in draft turn 1 (no picks). Draft: first call ~979k, later ~100k;
one BFS per spawn/camp group in the first call: rows 156k, corners 471k, lanes 486k, expanse 647k.
Camp `spawn_position()` readable in draft; live `position()` throws until visible.
