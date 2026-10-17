# Minimal cache, spacing and LIGHT channel regressions

Requires Python 3.11+, an exception-enabled WASI SDK, the official CAMBC C++ SDK,
and the Python `wasmtime` package from `requirements.txt`. No game CLI, network,
account or fixed workspace path is needed.

```sh
python run.py --src /path/to/bot/src --sdk /path/to/sdk/cpp \
  --compiler /path/to/wasi-sdk/bin/clang++ --report results.json
```

Windows uses `clang++.exe`. Optional arguments are `--wasi-sdk` (toolchain root),
`--wasmtime-pythonlib` (existing package directory), `--jobs 2` (parallel compiles)
and `--build-dir /path/to/scratch` (retain diagnostic artifacts). Otherwise scratch
files are temporary. Source and reports/build directories must be separate.

For all eight combinations of `P_DP_MEMORY_FIX`, `P_DP_ANCHOR_FIX` and
`P_DP_CHANNEL_FIX`, the runner copies source into scratch, overrides only those
three definitions in scratch `params.h`, then:

- Compiles the complete production `main.cpp` against the supplied official SDK.
- Executes one combined WASI fixture using the actual `draft_plan.h` and
  `channel_safety.h`, plus the actual three channel eligibility/action functions
  extracted verbatim from the supplied `main.cpp`.
- Tests cache failures, strict admission, atomic state, independent legacy
  settings, short-write retained-tail invalidation, budget fallback, first-SDK-tile
  tie stability, second-anchor spacing, local channel exposure, awake camps,
  post-move observations and command acceptance.
- Verifies normal geometry/bank equality with memory off/on and verifies that
  supplied source and fixtures remain unchanged throughout the run.

The channel fixture enables the existing optional `P_TRIBSAFE=5` distance gate to
exercise its post-move check; complete production compilation uses the supplied
settings. The fixture's ordinary submission cases retain survivable current damage
and do not invent future enemy or personal camp damage forecasts.

Memory tests remain separate from channel mocks and assertions. Algorithms are
included/extracted from production source; mock geometry and SDK faults are test
inputs. These tests run no matches and establish no playing strength, universal
fuel bound, whole-channel survival guarantee or untested native contract. The
production object compile is not the official release build/link.

Publish only this README, runner, requirements, `.gitignore` and three fixture
sources. Generated objects, WASM, logs and `results.json` are ignored. The earlier
full-forecast v2 test package is preserved separately as experiment evidence.
