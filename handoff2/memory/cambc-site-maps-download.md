---
name: cambc-site-maps-download
description: The full current site map pool (35 maps) downloads without login via curl; copy at arena/maps/site35; cambc 3.0.2 local arena setup steps
metadata:
  type: reference
  modified: 2026-10-20T22:14:37.099Z
---
2026-10-20 22:11 UTC: GET https://2026a.battlecode.co.uk/api/v1/maps/pool (no sign-in) lists {id,name,sha256,size}; each map is at /api/v1/maps/pool/<id>/file (303 redirect, use curl -L). `cambc init`/`maps pull` fails here (rustls UnknownIssuer through the proxy), curl works.
2026-10-21 23:20: pool is 40 maps, saved to /mnt/project-files/arena/maps/site40 (sha-verified; the 35 old ones byte-identical to site35, 5 new: gem_fields, gemfight, great_wall, lost_world, road_of_riches).
All 35 maps (sha-verified) saved to /mnt/project-files/arena/maps/site35/<name>.map26a (prefix 00/01 dropped).
cambc 3.0.2 from PyPI = engine 1.0.1 (summary match.engineVersion "1.0.1"); 3.0.3 exists on PyPI too (unchecked). Toolchain: curl wasi-sdk-33, cmake 3.31.8, ninja 1.12.1 into /root/.cache/cambc as in [[cambc-arena-setup]]. A game on 3.0 takes ~30 CPU-s; 70 games on 4 cores ~5 min with CAMBC_WASMTIME_CACHE. `cambc run-batch MANIFEST --jobs 4 --release`, manifest rows `botA botB map out.repl26a --statistics out.json --json`. Summary JSON has events kinds death / fuelExhausted / botFault / wardPlacement. Old hold60 maps still load.
