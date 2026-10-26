---
name: cambc-teammate-sdk3-osc-1021
description: 2026-10-21 teammate's bot2_sdk3_compile_fix = v98 + only the camp-probe fix; local vs v98 site35 37-33, hold60 65-55 (flat)
metadata:
  type: project
---
Mac folder ~/Downloads/bot2_sdk3_compile_fix holds bot2_frozen (= v98, cosmetic golem-fallback edit for stale SDKs) and bot2_camp_oscillation_fix_v1 (= v98 + only the camp-probe fix, i.e. change 3 of [[cambc-teammate-dash-survival-1021]]). v98 already compiles on cambc 3.0.4; the "compile fix" is only for the teammate's stale local SDK.
Local 3.0.4 --release vs v98: site35 37-33 (both 9 / none 7 / split 19), hold60 65-55; gems, deaths flat. The dash_survival bot's +8 net maps comes mostly from its dash/engage changes, not the camp fix.
Files analysis/teammate-bot2-sdk3-1021/. Nothing uploaded.
Run note: CAMBC_WASMTIME_CACHE must be an absolute path (value 1 makes every game fail).
