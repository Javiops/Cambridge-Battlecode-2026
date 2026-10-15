# study27: stack on big camps, spread on small ones

study27 = study26 + one rule about when several champions farm the same camp.

`bots/study27` is `bots/study26` renamed and edited in place, so `git diff` shows only the changed lines (9 in
`main.cpp`, 3 in `params.h`). study26 itself stays in the history (`git show 5a9229b:bots/study26/src/main.cpp`).

## The rule, step by step

Every 20 rounds (or when its camp is done) each champion scores every camp group and walks to the best one
(`choose_target` in `main.cpp`). The score is roughly `value / rounds`:
- `rounds` is the walk, the kill time and the capture.
- `value` is the camp's gems shared by the champions already going there plus this one (`team`).

1. study26 shares a camp's gems evenly: `value = gems / team`. A champion joining one ally values the camp at half,
   so champions almost always spread out, even on camps that take one champion 40+ rounds to kill.
2. study27 keeps that for small camps. A camp is "big" at 3000+ hp (`P_STACK_HP 3000`): 2-3 elks, an elk with
   wolves, or 3 wolves. That is about 1 camp in 4. Single wolves or elks, 2 wolves and gem clusters stay small.
3. On a big camp a joiner values it at `gems / team^0.75` (`P_SHAREEXP 75`): with one ally already there it is
   worth 59% instead of 50%, with two 44% instead of 33%.
4. Up to 4 champions may claim a monster camp (`P_MAX_SHARE 4`, was 3).

So a champion joins a big camp an ally is killing when that beats walking to a free camp. On small camps it still
goes alone.

What changes in play (106 games, official 9 + gen 44, study27 vs study26 in the same games):

| | champions per kill, small camps | rounds per kill, small | champions per kill, big camps | rounds per kill, big | big camps killed |
|---|---|---|---|---|---|
| study26 | 1.40 | 11.6 | 2.02 | 26.7 | 207 |
| study27 | 1.43 | 11.6 | 2.42 | 21.5 | 264 |

## Results

`tools/ab.py`, from both sides; only maps won (or lost) from both sides count.
- v100 = 100 maps from genmaps seed 1015.
- f150 = 150 maps from seed 31337, made after the settings were chosen.
- Both are in the project folder at `arena/maps/`.

| set | maps | won both | lost both |
|---|---|---|---|
| official | 9 | 2 | 1 |
| gen | 44 | 14 | 7 |
| hold60 | 60 | 20 | 9 |
| dev200 | 200 | 54 | 43 |
| v100 | 100 | 26 | 20 |
| f150 | 150 | 38 | 26 |
| **all** | 563 | **154** | **106** (p < 0.01) |

It is ahead on every set. Same rule on study25: 154 / 102.

## Where the line is (tested on study25)

| variant | won / lost both, 413 maps |
|---|---|
| big = 2400+ hp (single elks and wolf pairs stack too) | 125 / 120: the gain is gone |
| big = 3000+, exp 0.5 | 125 / 88 |
| big = 4000+, exp 0.5 | 118 / 85 |
| big = 3000+, exp 0.25 (stack harder) | 107 / 100 |
| **big = 3000+, exp 0.75 (study27)** | **120 / 75** |
| Mite's squad sizes taken literally: 2 on every small camp, 4 on big | 68 / 138 |
| whole team on the first camp before round 50 | 89 / 75 (no clear gain); on top of the rule 120 / 111 |
| a champion waiting for a respawn joins another camp instead (`P_NOIDLE` 0 / 2 / 5) | 45 / 131, 40 / 127, 52 / 120 |

Map-wide features (camps per champion, spacing between camps) do not say when stacking pays. A split that looked
good on hold60 and dev200 reversed on v100. What matters is the size of the camp.

Waiting next to a camp that is about to respawn is right. The champion is already where the next capture will be.
Leaving turns the wait into walking and loses that capture.

Zip: `bot/mybot_study27.zip` in the project folder.
