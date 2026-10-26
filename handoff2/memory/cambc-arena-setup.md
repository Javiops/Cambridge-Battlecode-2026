---
name: cambc-arena-setup
description: Local CAMBC arena works in this project: official cambc CLI 2.1.2 from PyPI, toolchain cache layout, real competition maps extracted from replays, how to run matches
metadata:
  type: project
---

The CAMBC CLI is the PyPI package `cambc` (2.1.2 on 2026-10-13; wheels for manylinux x86_64,
win_amd64, macOS arm64; one native binary at `cambc-2.1.2.data/scripts/cambc`). Commands:
`init`, `new --lang cpp`, `build BOT`, `run BOT_A BOT_B --map X.map26a -o DIR --rounds N
--statistics stats.json`, `run-batch` (manifest: bot-a bot-b map replay; --jobs), `view`,
`bundle`, `maps pull`, `mapeditor`. Set `CAMBC_NO_UPDATE_CHECK=1`.

In a fresh cloud session the toolchain must be re-fetched by curl (the binary's own
downloader fails TLS through the proxy): wasi-sdk 33 -> `/root/.cache/cambc/wasi-sdk-33/`,
cmake 3.31.8 -> `/root/.cache/cambc/cmake-3.31.8-linux-x86_64/`, ninja 1.12.1 ->
`/root/.cache/cambc/ninja-1.12.1-linux-x86_64/ninja`. `cambc init` then builds C++ bots fine.
`cambc maps pull` cannot work here: 2026a.battlecode.co.uk is blocked by the egress policy.

Maps: the five official maps from the user's 0-5 replays (3, 4 and 5 champs per team) are
saved in `/mnt/project-files/arena/maps/official{1..5}.map26a`; `arena1.map26a` is a synthetic
60x60 map. Tools in `/mnt/project-files/arena/tools/`: `extractmap.js` (replay -> map: the
`.map26a` bytes sit verbatim at offset 14 of a raw replay, after the `a62per` header) and
`mkmap.js` + `arena1.json` (build maps by driving the editor's wasm `MapBuilder_*` API).
A replay bundle (`.repl26a` from `cambc run`) is a zip holding replay.repl26a and
team-a/b.stdout/.debug. A full game runs in under a second.

Baseline 2026-10-13: the bot in [[cambc-bot-project]] beats starter-cpp 5/5 on the official
maps (1000 gems by round 486-1081), so the starter is too weak to be the benchmark.

**Why:** rebuilding this setup cost hours; future threads should reuse it.
**How to apply:** copy the maps into a cambc workspace `maps/` dir and run `cambc run`;
use run-batch for tuning. See [[cambc-user-prefs]].

2026-10-14: cambc 2.1.6 on PyPI. With SSL_CERT_FILE=/root/.ccr/ca-bundle.crt, `cambc init --yes` pulls the 9 maps,
but the wasi-sdk download still fails TLS: fetch wasi-sdk/cmake/ninja with curl as above (wasi-sdk tar
extracted with --strip-components=1). Copying a built bot dir breaks `cambc build` (stale .cambc CMakeCache).
