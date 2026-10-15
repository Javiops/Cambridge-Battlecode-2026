# Data for the #1/#2 dissection (2026-10-15)

Root: `/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad` (call it `$S`).

## Games
`$S/ws/selected.json`: list of 108 records (101 distinct matches; a match can appear for both teams).
Fields: `match` (id), `team` ("mite" = ladder #1 Mite, "uni" = #2 Univardisty of Shingtonwash), `side` ("a" = team 0, "b" = team 1),
`map` (one of collision corners elkring expanse interlock lanes monolith packs rows), `opp` (opponent name), `orank`, `res` (win/loss),
`score`/`oscore` (tributed gems), `rounds`, `created`, `draft` (list of champion_draft enum ids in pick order:
0 ryth, 1 vesper_vale, 2 vendetta, 3 cassi_and_issac, 4 stellar, 5 prism, 6 marcella, 7 willow, 8 ren, 9 varg, 10 tavi).
6 games per team per map, each vs a different top-20 rival, played 07:00-08:28 UTC today. The engine is deterministic.

## Per-game decoded events: `$S/ws/steps/<match>.c.jsonl`
One JSON object per line, two kinds:
- `{"t":"round","r":R,"sub":[gemsA,gemsB],"champs":[[index,team,typeName,x,y,hp,maxhp,gems,gold,alive],...],"camps":[[index,typeName,x,y,hp,alive,awake,group],...]}`
  = snapshot at the END of round R (the line is written when the round changes, so it appears after the round's events). Round 0 = spawn state.
  Champion index is global (team 0 champions first). Dead champions have x,y = -1. Camp `group` = camp-group index (a group = one capture unit).
- `{"t":"ev","r":R,"ph":PHASE,"k":KIND,"ak":ACTORKIND,"a":ACTORINDEX,"apos":[x,y],"eff":[...],"keff":[...]}`
  = one engine step that changed something or was a champion action. `ak` 1 = a champion acted (`a` = its index, `apos` = its position after the step),
  `ak` 2 = a camp monster acted, `ak` 0 = engine phase (e.g. ph 7 = camp captures, ph 1 = camp respawns).
  `k` (step kind, observed): 4 move, 5 basic attack, 6 ability cast (spell / dash / attack reset / stun), 13 buy item, 14 ?, 18 start tribute,
  11/12/20/23/26 other actions (recall start, ward, cancel...; infer from effects), 1 respawn. ph: 10 = champion turn, 14 = champion start-turn, 13 = champion end-turn
  (hp regen / channel completion), 9 = camps acting, 7 = captures, 4 = spells phase.
  `eff`: champion changes caused by the step: `{"i":idx,"hpnow":hp, "hp":delta, "pos":[x0,y0,x1,y1], "gems":delta, "gold":delta, "alive":0/1, "maxhp":delta}`.
  So a basic attack by `a` with eff hp<0 on idx j = j was hit. A cast (k 6) with several negative hp effs = area spell; with a pos eff on `a` itself = dash;
  with no eff = attack reset / stun (stun has no direct damage; Cassi slot1, Ryth slot0 has damage). A move (k 4) of >1 tile with ph 14 = recall arrival or respawn.
  Gold delta <0 at k 13 = purchase (shards cost 30, consumables vary); gems delta >0 at ph 7 = capture; gems -> 0 at ph 13/14 near an altar = tribute done.
- Recall: starts with an action (no visible effect) and the champion jumps to spawn 5 turn-ends later (pos jump at ph 14). A damage hit interrupts it.
  Detect recalls as a position jump to the spawn area of >2 tiles while alive (not a respawn, which has alive 0->1).

Tools that already parse this format: `$S/tools/micro/*.py` (fights.py, fightstats.py, actions.py, chase.py, disengage.py, spread.py, idle.py, seqs.py)
written for the same compact format on 2026-10-13; reading their first 40 lines shows how to load rounds/events. Reuse their loaders.

## Maps: `$S/ws/mapsj/<map>.json`
`{w,h,sym,nch (champions per team),spawnA:[x0,y0,x1,y1],grid:[rows of chars: '#' wall, 'o' hole, 'A' altar, '"' bush, '.' floor],camps:[{type,x,y}],groups:[{gems,gold,respawn,n,camps:[camp idx]}]}`.
Team B spawn = mirror of spawnA by `sym`. Movement is 8-directional (Chebyshev), 1 tile per turn; walls block. Distances: BFS on the grid.

## Rules: `$S/docs/GameRules.md` (champion kits with spell multipliers, ranges, cooldown 8, recall 5 ticks, tribute ceil(gems/10) ticks, death 60 rounds,
killer takes the victim's gems + 50 gold), `$S/docs/BotAPICpp.md`. Item ids (order of `itemsBought` in stats) in `/mnt/project-files/analysis/data/items.txt`.
Measured engine facts: monsters focus one champion; only champions on the group's spawn tiles share the capture reward; a ranged champion that attacks
cannot move that turn; "exclusive" spells cannot be cast after moving that round (Stellar damage+AoE, Tavi, Cassi damage); vision 8.

## Earlier findings to build on (do not redo)
- `/mnt/project-files/analysis/top1-cycle-2026-10-15/README.md`: farming camp set, nearest-camp-up rule, recall-as-teleport, camp evaluator (same 101 games).
- `/mnt/project-files/analysis/top1-2026-10-14/como-juega-el-numero-1.md`: Univardisty fights, casters at range 4, recall below 30% hp (yesterday's games).
- `/mnt/project-files/analysis/top10-2026-10-14/how-the-top-10-play.md`.
