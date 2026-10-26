---
name: cambc-site-access
description: The competition site 2026a.battlecode.co.uk was blocked from the default cloud environment; on 2026-10-13 the user added a cloud environment with that domain allowed, so threads started after that can reach it
metadata:
  type: project
---

`cambc maps pull`, `cambc login/submit` and the match pages all live on 2026a.battlecode.co.uk.
Sessions on the project's built-in environment get HTTP 403 from the egress proxy for that
host (do not retry or route around it). On 2026-10-13 ~11:40 UTC the user created a cloud
environment (env_01HoGhLeVW1qVKs6Tj73n5iM) with the domain in Allowed domains and selected it
for the project; only threads started afterwards run on it. Viewing the user's own matches
still needs their site login (cambc login or a browser session), which they must provide.

**Why:** the first thread wasted time on the block and had to extract maps from replays instead.
**How to apply:** in a new thread, test `curl -sS -o /dev/null -w '%{http_code}' https://2026a.battlecode.co.uk/`
first; if it is reachable, `cambc maps pull` gives the full official map pool for the arena in
[[cambc-arena-setup]].

Checked from the new environment (2026-10-13 11:45 UTC): reachable. Public without login:
`/api/v1/event/status` and the map pool. Run the cambc CLI with
`SSL_CERT_FILE=/root/.ccr/ca-bundle.crt`; `cambc maps pull` needs a `cambc.toml` in the cwd
(empty file works). Pool of 9 maps saved in `/mnt/project-files/arena/maps/pool/`
(collision/rows/corners/lanes/expanse = official1..5; new: elkring, interlock, monolith, packs).
`/api/v1/submissions` and the `/game/` app need sign-in. Use `cambc login` (device link the user
approves at /game/cli-login) only after the user says yes; never store the token anywhere shared.
Result: `cambc login` works, but its token (Bearer) is only accepted for bot upload; GET
`/api/v1/matches`, `/teams/...`, `/submissions` still answer 401. CLI 2.1.2 has no command to
request or list matches. `/api/v1/ladder` is public (65 teams on 2026-10-13). All matches and replays
are public through other endpoints, see [[cambc-public-match-data]].

Unranked matches (found 2026-10-13 18:20 UTC from the web app JS): the site starts them with
`POST /api/v1/challenges {teamId, sourceGroupId?, mapIds?}` (5 maps, team hourly quota, list with
GET /challenges) and always plays the team's ACTIVE submission (`PUT /submissions/active
{submissionId}` switches it). So an online test of a candidate means making it the active bot; the
user does it (upload + "Play an unranked match" in Matches) and Claude reads the results from the
public match-groups API. The CLI 2.1.2 has no match command (Blue Dragon's `cambc match unrated`
was an older CLI). Static JS needs the CloudFront cookies set by any /game/ page (curl -c jar).


2026-10-13 19:20 UTC: the user chose the "full loop" (Claude uploads each candidate that wins locally,
the top 10 get challenged, results analysed). `cambc login` approved by the user; token in the
container only (/root/.config/cambc). CLI 2.1.5 (newest on PyPI) still has no ladder/team/match
commands. The token works for `cambc submit` (study4 = version 12) but every other API call
(/challenges, /submissions GET, /me) answers 401, so making a version active and starting unranked
matches stays a click for the user on the site. Fetch our results with `ws/tools/fetch_ours.py`.
20:05 UTC: POST /challenges needs an Origin header (else "Origin rejected") and a web session (CLI
Bearer -> 401). The web sign-in redirects to battlecode.co.uk/auth/signin, which this environment's egress
blocks (403), and it needs the user's own browser login anyway: launching matches stays the user's click.
2026-10-19 00:09 UTC (user authorized in the loop thread 23:59 UTC for that night): `cambc submit <bot>` from a workspace (bots/<name>/src) uploads AND selects the new version (status queued -> active after compile); PUT /api/v1/submissions/active {submissionId} with the web event_session cookie switches versions (old ones too). The selected version plays matches once queued (v71 groups sent while queued were labelled v71). online/overnight_pair.py runs v65 draw -> candidate -> v65.
