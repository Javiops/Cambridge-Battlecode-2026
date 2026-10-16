# Development harness: how an idea becomes the bot

Four stages, each with a gate that has numbers. Nothing enters the next stage without passing the gate, and
everything that goes through gets recorded on the board ([IDEAS.md](IDEAS.md)) with its stage and its result.

```
 1. brainstorm  ──►  2. development + local test  ──►  3. online (hours: ranked + 30 challenges/hour)  ──►  4. dissection
    ideas with a         one idea = one branch,           paired A/B against the same 30 teams,               metric scorecard
    hypothesis           tools/gate.py decides            online/lfl.py decides                               and proposals ──► 1.
```

Every step is a one-line command that already lives in the repo; this document says when each one runs, which
number has to come out to move on, and where what it produces is kept.

## House rules

1. **One idea, one branch, one change.** Branch `idea/I012-short-name`, editing the current bot in place
   (`bots/study27-economy/src`, never a new copy under `bots/`: the PR diff is the change and nothing else). To test the
   idea against the base, `gate.py` exports the `main` version by itself (`python3 tools/gate.py bots/study27-economy main ...`).
2. **The online bot only changes with an idea in stage `local-ok`**, recorded on the board, and at most once an hour
   (each online hour is a 150-game sample; two changes in the same hour cannot be told apart).
3. **The gate decides, not the feeling.** A result without its `gate.txt` (local) or its `lfl.py` output (online) is
   not a result. The gate numbers are below; an idea that does not reach them stays in its stage or closes as
   `rejected` with the number that closed it.
4. **Nobody touches a teammate's work.** Everyone works on their own branch and puts their ideas through the same
   gate; ideas get combined in stage 2 (see "combinations"), never by editing someone else's branch.
5. **Everything goes on the board.** `python3 tools/idea.py add|set` at every stage change. The board is what the
   coordinator reads for the hourly summary and what anyone looks at to know where we are.
6. **At most 3 ideas in `dev`/`local-test` per person.** With more, nobody finishes any.

## Stage 1: brainstorm

**In:** the latest dissection scorecard (`online/data/dissect/<version>/scorecard.md`, stage 4), the `lfl.py` output
of the last idea tested online, the top-team studies (`/mnt/project-files/analysis/`, summary in
[current-state/](../current-state/README.md)) and what was already tried ("Closed" section of the board: no repeats).

**Out:** ideas on the board with a measurable hypothesis. Template: [templates/brainstorm.md](templates/brainstorm.md).

```bash
python3 tools/idea.py add "Two champions per camp on fight maps" --kind fight \
    --source "corners-fix scorecard 15 Oct: 22% of hits taken with no ally within 8" \
    --hypothesis "hits taken with no ally within 8 from 22% to 12%; deaths/game from 5.5 to 4.5 on corners/collision/packs"
```

Rules: every idea names **which scorecard number it moves and by how much** (if it cannot be measured it is an
opinion, not an idea); says **on which maps** it applies; is **one change** (one rule, one threshold, one switch). A
combination of ideas is another idea, opened only once its parts have a result.

**Gate to development:** a hypothesis with a number, a kind (`farm`/`fight`/`macro`/`bug`), someone assigned
(`--owner`). Whoever takes it moves it to `dev` with their branch.

## Stage 2: development and local test

A "subagent" is whoever takes the idea: a person or a Claude thread. They get the brief from
[templates/brief.md](templates/brief.md) (idea, hypothesis, base bot, the gate it has to pass, what to deliver) and
stay inside it: make **their** idea work, not improve the bot in general.

```bash
git checkout -b idea/I012-two-per-camp main
python3 tools/idea.py set I012 --stage dev --branch idea/I012-two-per-camp --owner Javi
#   ... edit bots/study27-economy/src (a P_* switch in params.h if it is a threshold: tools/variante.sh helps try values)
python3 tools/gate.py bots/study27-economy main --kind fight --idea I012        # the gate; ~1-3 min on 4 cores
```

`gate.py` runs in phases, cheapest first, and stops as soon as the result is clear:

| phase | what it plays | stops if | time (4 cores, warm cache) |
|---|---|---|---|
| 1 safety | 9 official maps x 2 sides + fuel on lanes/corners/collision | bot faults > 0, a broken game, or +30 fuel-exhausted turns over the base | 20 s |
| 2 fresh maps | hold60 + dev200 (+ `--extra fresh300`) shuffled, in chunks of 40, maps won **on both sides** | worse with p<0.05 (any kind); better with p<0.01 (farm) | 10 s per chunk |
| 3 panel | spar11/12/16 (the only local rivals that kill like online teams) on official + gen | the games that flip go against with p<0.05 = **veto** | 60 s |
| 4 counterexamples | the fresh maps lost on both sides, with the command to watch them | always written | 0 |

**Gate to `local-ok`:**

| kind | fresh maps (phase 2) | safety | panel |
|---|---|---|---|
| `farm` / `macro` | in favour with **p<0.05** (about +6 net maps out of 44 decided, +10 out of 100) | clean | no veto |
| `fight` | **not worse** (p>=0.05): local play cannot judge a fight rule (it is self-play, see memory `cambc-online-ab`) | clean | no veto |
| `bug` | not worse | clean, and the bug no longer reproduces on its counterexample | no veto |

The verdict comes out on its own (`PASS` / `FAIL` and why) and stays in `out/gate/<cand>_vs_<base>/gate.txt`,
`result.json` and `counterexamples.md`; with `--idea` it is recorded on the board.

Rules of the stage:
- **Counterexamples before celebrating.** Before moving to `local-ok`, watch the 3 worst counterexamples with
  `cambc view` and write one line per map in the idea's doc (why it loses there and whether it matters).
- **Time.** The caches (`out/ab-cache`, `out/wasmtime-cache`) mean the base and the panel are never replayed: the
  second candidate costs only its own games. `--max-maps 80` for a first look; the full gate to decide. Never tune
  a threshold by looking at hold60/dev200 (they are the sealed check); tune on `maps_gen` or `--extra`.
- **Safety** = bot faults (`botFaults`), broken games, fuel (`tools/replaydump.js` counts the kind-26 turn ends), and
  no per-turn scan of every camp or champion (memory `cambc-fuel-budget`).
- **Combinations.** A combination (two switches, two branches merged) passes the same gate **against the best of
  its parts**, not against the base: if it does not beat the best part, keep the part.
- **The base is the online bot, checked by hash.** Register every upload with its zip:
  `python3 online/version.py "v38 = I012" --zip /mnt/project-files/bot/mybot_I012.zip`. Then
  `gate.py bots/CAND online` plays against that exact zip, and every gate run prints whether its base is the online
  bot (`python3 tools/online_base.py bots/X` checks a folder by itself). A PASS against any other base does not
  clear an upload. (16 Oct: a morning of gate runs used `main` while the online bot was another branch.)
- **Site maps.** `cambc init --yes` pulls the site's current pool into `maps/` (17 maps on 16 Oct; older setups
  have 9): rerun it when the site adds maps. Phase 1 lists every site map as won (+), lost (-) or split (=) on both
  sides, so a candidate that breaks a real map is seen by name.
- **What local cannot see**: how the top teams fight. That is why a fight rule with a local `PASS` is in `local-ok`,
  not `accepted`; stage 3 decides it.

**Deliverable of the stage:** a PR with the bot diff + `docs/<I012-name>.md` following
[templates/result.md](templates/result.md) (hypothesis, change, gate table, counterexamples watched). The PR is not
merged until the online decision (stage 3), except for `bug` and `infra`.

## Stage 3: online (several hours, ranked + 30 challenges per hour)

Only an idea in `local-ok` goes in. A person always does the upload (uploading and activating on the site is a live
action): bundle, upload, activate and register the version in the same minute.

```bash
cambc bundle bots/study27-economy --output /mnt/project-files/bot/mybot_I012.zip   # 1. the zip (in the repo, on the idea's branch)
#   2. upload and ACTIVATE on 2026a.battlecode.co.uk (a person)
python3 online/version.py "v38 = I012 two per camp"                         # 3. games from that minute belong to I012
python3 tools/idea.py set I012 --stage online --version "v38"
```

The challenge loop (`online/loop.py --top 30`, or the scheduled task at :46 UTC that already runs) spends the 30
groups of the hour against the same 30 top teams; `collect.py` downloads the results. **A/B protocol:** the candidate
and the base alternate hour by hour (A, B, A, B...), at least **2 hours each** (about 300 games and ~200 shared
opponent+map pairings); every batch is compared as soon as it lands:

```bash
cd online && python3 collect.py && python3 lfl.py --a "I012" --b "study27" --idea I012
```

`lfl.py` counts only the (opponent, map, side) pairings played with both versions (the engine is deterministic: a
pairing is a controlled experiment) and runs the sign test on the pairings that flip. The raw percentage of a batch
is **worthless** (today it went from 25% to 41% without touching the bot: the opponent draw changed).

**Gate:**

| `lfl.py` result | decision |
|---|---|
| A better with p<0.05 | `accepted`: the branch merges into `main` (rename + diff, never a new copy) and stays as the online bot |
| A worse with p<0.05 | `rejected` with the number; the base goes back on the site next hour |
| undecided after 3 hours each (6 batches) | `rejected` as "changes nothing", unless it is `farm` with a clear local `PASS`: then `accepted` as neutral (farming is measured well locally) |

Meanwhile the ranked games of the window (about 20 an hour) are only a check that nothing sinks: 20 games an hour
decide nothing. Also watch `faults` in `games.jsonl`: a bot fault online is `rejected` on the spot, whatever the score.

Rules: no other idea goes up while one is in stage 3 (the samples would mix); when the cookie expires
(`challenge.py` returns 401) a person renews it (README in `online/`) and the lost hour does not count.

## Stage 4: dissection and new ideas

When an idea finishes stage 3 (or every morning with the active version), the scorecard:

```bash
cd online && python3 collect.py && python3 dissect.py --version "I012" --ref "study27" --idea I012
```

`dissect.py` downloads the missing replays, decodes them (about 25 s per new game, 4 at a time, cached) and writes
`data/dissect/<version>-<date>/scorecard.md`: the same metric for us and for the rival in the same games (deaths and
how we die, dead/idle champion-rounds, captures per champion-round, contact before the first hit, openings alone,
spells, fuel), by map and by rival tier, with the previous version as an extra column when `--ref` is given. The
scorecard ends in **Proposals**: the biggest gaps against the rival, as sentences that go straight into
`idea.py add`. With that, back to stage 1.

For finer questions (why we die on corners, what the rival does on lanes) the workspace `dissect.py` leaves
(`selected.json`, `steps/`, `mapsj/`) is the same format the scripts in
`/mnt/project-files/analysis/v35-dissection-2026-10-15/scripts_*` read (`WS=<folder>`); long analyses go to
`/mnt/project-files/analysis/<topic>-<date>/README.md` and are linked from the idea.

## Who does what

| | brainstorm | development + local | online | dissection |
|---|---|---|---|---|
| Javi | decides which ideas go in and in what order; assigns | own ideas through the gate | uploads, activates, registers the version; decides with `lfl.py` | reads the scorecard |
| teammate | proposes with a hypothesis | own ideas through the same gate, on their branch | same, when their bot is the active one | |
| Claude threads | propose from the scorecard and the studies | one thread per idea with the brief; delivers PR + doc + gate.txt | the loop thread sends the challenges and runs `lfl.py` every hour | `dissect.py` and the finer questions |
| coordinator | | summarises the board in the project chat (ideas per stage, last one that moved) | says when `lfl.py` decides | |

## Where everything lives

| what | where |
|---|---|
| ideas board | `harness/ideas/I###.json` (one file per idea, merges without conflicts) and `harness/IDEAS.md` (generated: `idea.py board`) |
| current bot | `bots/study27-economy/src` on `main`; online version in `online/data/versions.jsonl` |
| local gate | `tools/gate.py`, results in `out/gate/<cand>_vs_<base>/` (gate.txt, result.json, counterexamples.md); loose A/B: `tools/ab.py` |
| maps | `maps/` official (cambc init), `maps_gen` (training), `maps_hold60` + `maps_dev200` (sealed, they decide), `/mnt/project-files/arena/maps/fresh300` (`--extra`) |
| panel rivals | `bots/spar11`, `spar12`, `spar16` |
| online | `online/` (collect, challenge, loop, report, lfl, version, dissect); data in `online/data/` (in the cloud: `/mnt/project-files/online/data/`, `games.jsonl`, `hourly.md`, `versions.jsonl`) |
| uploaded zips | `/mnt/project-files/bot/mybot_<idea>.zip` |
| dissection scorecards | `online/data/dissect/<version>-<date>/scorecard.md` |
| long analyses | `/mnt/project-files/analysis/<topic>-<date>/README.md` |
| doc of each version | `docs/<I###-name>.md` (template `harness/templates/result.md`) |
| team memory (lessons) | project memory (`cambc-eval-method`, `cambc-online-ab`, `cambc-fuel-budget`...) |

## Set up the environment (once)

```bash
pip install cambc && cambc init --yes          # SDK, toolchain, the 9 official maps in maps/
cambc build bots/study27-economy && cambc build bots/spar11 bots/spar12 bots/spar16
python3 tools/gate.py bots/study27-economy bots/study25 --kind farm --max-maps 40   # smoke test: ~40 s, should say "in favour but undecided"
```
In the cloud, when `cambc init` cannot download the toolchain (certificate), fetch it by hand into `~/.cache/cambc/`
(`wasi-sdk-33`, `cmake-3.31.8-linux-x86_64`, `ninja-1.12.1-linux-x86_64`) and run it again.
