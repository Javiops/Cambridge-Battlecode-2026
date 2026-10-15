STUDY28 EVALUATION RECORD

Baseline: 43d003323cd16059cda6a54de14ed86e2da3b788.

results.txt explains every isolated change, combination, direct ablation and the final confirmation. experiments.json.gz contains all 12,888 unique game outcomes, hashes and stage membership. validation.json records the frozen source and independent audit. confirmation-maps.zip contains the 1024 newly generated maps and their manifest.

Only the capture_handoff guard is retained in the production bot. It was frozen before map generation; final confirmation was 1049 wins and 999 losses over 2048 games, a modest 51.2% against the original. The paired-map sign test is 80 both-won versus 55 both-lost, p=0.03847.

Reproduction instructions and independent patch functions are in tools/study28_fixes. Replaying disclosed deterministic games is reproduction, not additional independent evidence.
