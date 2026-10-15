# Online testing loop (unranked challenges + results)

What Mite does: ~27 challenge groups an hour against the top teams, all day. This folder does the same for our team
("Live Love Larp") with the site's public API plus your browser login. Everything is standard Python 3 (no packages).

## Files
* `collect.py` — downloads every finished match group of our team (public, no login): one row per game in
  `data/games.jsonl` (time, kind, opponent + rank, map, side, result, gems both sides, drafts, faults, replay URL),
  full statistics in `data/groups/<id>.json`, map ids in `data/maps.json`. `--replays` also saves replay bundles.
* `challenge.py` — starts unranked matches with the ACTIVE bot: reads the hourly allowance from the site, picks the
  opponents we have played least recently among the top N (`--top 20`, or `--targets Mite,hello`), skips teams the
  site says are out of our rank range, optional `--maps rows,corners`, `--dry-run` to only print the plan. Needs the cookie.
* `report.py` — win rates by map, opponent, tier and hour: `python3 report.py --since 2026-10-15T11:00 --kind unranked`.
* `loop.py` — every 10 min collect, every hour challenge. `python3 loop.py --top 20` (or `--no-challenge`).

## The login (what the scripts cannot get by themselves)
The site only accepts challenge requests from a signed-in browser session; the CLI token does not work for this.
Once, in the browser where you are signed in to 2026a.battlecode.co.uk: open DevTools (F12) > Network, click any
request to `/api/v1/...` (reload the Matches page), Request Headers, copy the whole value after `cookie:`.
Put it in one of: environment variable `CAMBC_COOKIE`, a file named by `CAMBC_COOKIE_FILE`, or `~/.cambc_cookie`.
Keep it private: anyone with it can act as your team on the site. It expires when you sign out or the session ends;
`challenge.py` then fails with 401 and you repeat the step.

## Where to run it
On your own PC it runs as long as the PC is on (`py loop.py --top 20` in this folder). In a cloud thread it runs only
while that thread's container lives, so the PC is the reliable place; the data folder is the same either way if you
run it inside the project folder.

## What to look at
`report.py` after each hour: win rate per map and per opponent tier for the active version; compare two versions by
`--since` windows. Each unranked game is deterministic for a given (version, opponent version, map, side), so repeats
of the same pairing add nothing: the loop rotates opponents for that reason.
