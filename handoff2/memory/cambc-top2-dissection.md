---
name: cambc-top2-dissection
description: 2026-10-15 decision-by-decision dissection of #1 Mite and #2 Univardisty (draft, shop, opening, fights, targeting, spells, map control, recall, deaths); report path and the key rules found
metadata:
  type: project
  modified: 2026-10-15T10:05:45.510Z
---

2026-10-15 09:23 UTC the user asked to dissect the downloaded #1/#2 games meticulously. Report:
`/mnt/project-files/analysis/top2-dissection-2026-10-15/README.md` (synthesis) + six detailed reports
(draft_shop, opening, fights, targeting_spells, map_control, recall_survival) with scripts; decoded
every-step games in `data/steps.tgz` (format in `data/DATA.md`; k11 recall start, k12 tribute start,
k13 buy, k20 altar lock placed before own tribute, ph14 k18 tribute done). Also in the repo branch
claude/project-thread-ztmd0i under analysis/top2-dissection. Same 101 games as [[cambc-top1-cycle]].
Replays are re-downloaded with scripts/dl.py; decode with replaydump.js --every-step --camps to a file
(piping breaks with ENOBUFS) then tools/micro/compact.py.

**Key rules (measured):** Mite = fixed draft per map (Varg/Ryth/C&I/Ren/Stellar), stack the nearest camp,
one capturer, bank small bags on every altar pass (median 36), recall at hp<50% from 7 tiles even under
fire (retries, 44 camp interruptions), shop only alive on spawn, build jungle>durability>bruiser hp>power,
casts from 3, melee wall + clump, never chases, never raids. Univardisty = draft varies per game since
07:00 UTC, split 3+2 opening, casts from 4-5, kites with attack resets, recall only when no foe in vision,
shops while dead, build power>durability hp>power, raids enemy gem clusters on lanes, bigger bags
(median 44, 12.6% of gems lost to deaths vs Mite 5.7%). Both: opener is a spell at 4-5 in ~90% of fights,
no waiting for numbers/hp advantage, prefer isolated victims, no chase, spells cast on cooldown (never
saved), focus one target 92%, elk first on camps, tribute instantly, no play-safe-when-ahead, no
territorial defence. Fights were even today (K/D ~1.0 both); Mite's edge = dying less. Head-to-head 5-2.
Related: [[cambc-top1-study]] [[cambc-understand-first]] [[cambc-eval-method]]
