# Reproduce the 1.0.2 patch checks

The frozen v19 source and all three bot WASM identities are unchanged. Runtime
pins are in runtime.json. Use official CLI 3.0.4 with a fresh initialized workspace,
release-build the frozen ZIP twice, and compare both hashes before running the
v19-lab.toml and v19-canary.toml schedules with tools/topdraft_screen.py.

For field captures, run tools/audit_field_102.py with explicit --journal, --maps,
--engine and --node paths. The journal is the batch.json beside collected group
folders. Maps come from the current official workspace. The engine must have the
recorded official SHA-256; Node.js 22 or newer is required. Completed captures are
checked; pending requests must be resolved first. The tool writes results.json
beside the journal and rejects older engine/replay bytes. Historical decoders and
Stage 1-7 runtime pins are preserved. See PATCH-1.0.2.md for the active collection
checkpoint and the validation archive for raw inputs and identities.
