# I033 budget/scouting evidence

Portable read-only ledger for 228 final native slots and 144 separate historical matched sparring controls. No native replay archives or executable binaries are bundled. The exact 16-file candidate source and frozen map bytes are included in ZIP files. Every ZIP was CRC-checked.

source-manifest.json and builds.json bind source, WASM and pinned runtime identities. final-games.csv records map, actual seed, statistics/archive/raw-replay/stdout hashes, outcomes and separate fuel/native-fault/caught-marker counts. caught-errors.json retains captured marker strings. Marker coverage may be selective or truncated; maximum reported counters are not additional complete event totals.

paired-map-outcomes.csv records both physical sides. matched-control-games.csv and matched-outcome-flips.csv contain historical controls on matching maps/sides; actual seed equality is shown, not assumed. Repeated native replay streams remain scheduled slots; the summary reports their unique count. They are not independent tactical discoveries.

mechanisms/ separates diagnostic/mock evidence from final strength samples. The rejected lethal-approach guard is absent from selected source. Intermediate tests retain original source hashes and final protocol binding; they are not retroactively called final-source builds.

The 96-map set was locked before these outcomes but comes from historical developer pools, not globally unseen tournament maps. No complete repository promotion gate, online A/B or activation was performed. This candidate is for draft review only and not ready for upload.
