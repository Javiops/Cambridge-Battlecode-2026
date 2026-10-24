# focus-v1 (on mgwp = v20c + mg1c + pw3 + waitpair)

Rule: a rival champion that lost health since last round with one of our allies within 3 of it gets a target-score bonus
(main target choice: -P_FOCUS_W on a score ~ hp + 40/tile; fight.h focus: -P_FOCUS_W/2). Foe::mate_hit, Seen::hp.
- fca: P_FOCUS_W 300; fcb: P_FOCUS_W 150. P_FOCUS 0 = mgwp behaviour.
Why: online near r30-150 (focus.py) top 10 vs V20: two hitters on one rival 25% vs 15% of hit rounds, 2nd hitter <=3r 33% vs 23%, kills with 1.82 vs 1.24 hitters.
Local near test (120 g each, vs mgwp gold r300 +171, loneliness 44%): fca +166 / 44%, fcb +161 / 45%. Focus metrics: pending.
Patches: diff_fca_vs_mgwp.patch, diff_fcb_vs_mgwp.patch (apply on mgwp or, without the waitpair/pw3 parts, on v20c: only main.cpp Foe/Seen/target score, fight.h, params.h).
