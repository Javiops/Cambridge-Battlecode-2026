---
name: cambc-fight-verdict
description: 2026-10-16 20:50 first-contact fight verdict: own hp predicts nothing (AUC 0.51), power ratio 0.65; P_PV switch (verdict.h) on v52 best +6/+9 flips, under the bar; report path
metadata:
  type: project
  modified: 2026-10-16T20:48:11.194Z
---

Thread "Decidir la pelea antes de empezarla" / "corte de pelea" (root cmsg_017gbamt2g1g8hMHRHQBc6qb6B7ZKmqZmwZX86KndvTxx7, session session_01VyqbNafnc37AyfQuqrJUBU; user 20:05: "leave when losing" is wrong, fights are decided before they start). Branch claude/fight-eval-9aa12v, no PR. Report /mnt/project-files/analysis/fight-verdict-2026-10-16/README.md (episodes csv, scripts, verdict_on_v52.patch).
- 63 online v52 games -> 1,843 fight episodes (first contact = enemy within 6): we lose 20% / win 19%; our rivals in those games lose 10% / win 36%; top 2 16% / 32%.
- At first contact own hp % predicts a lost fight at AUC 0.51 (nothing); team hp ratio 0.67, power (hp x dps, allies within 6) 0.65; all 18 features 0.71.
- Power < 0.8: 13% of fights, we lose 40% win 4%, = 26% of our losses; we stay 85%; leaving at once loses 24%; rivals leave 42% and lose 19%.
- 65% of our losses start favourable (power >= 1.25); enemies arrive later in 82% of them. Power > 4: we win 24%, top 2 41%: we do not convert won fights.
- P_PV (verdict.h + 3 guarded lines in main.cpp step 3 after the P_ALLYDUTY block, `if (pv_fight) favourable = true;` before g_ally_near_tgt, P_AVOIDFIRST order untouched; rule: below power 0.6 at first contact leave and do not return until allies arrive; leave verdict held until contact ends, hysteresis; P_PV 2 adds a fight verdict; 9 variants tested): P_PV 0 = 0 flips on both panels. Best `P_PV 1, P_PV_LEAVE 60, P_PV_ER 6`: flips vs v52 panel A (12:52) 17-11, panel B (v51) 20-11; deaths -0.5..-1.5/game; loses corners on B. Enemies counted within 8 instead of 6: B up to +17 but A -6. Not a win by [[cambc-panel-noise]]. Zip /mnt/project-files/bot/mybot_v52_verdict.zip, not uploaded (online test only if the user asks); patch sent to the fixes thread ([[cambc-teammate-fixes3-cases]]) via the coordinator as an optional switch to stack/measure.
**Why:** every earlier fight-or-flee attempt ([[cambc-danger-level]], [[cambc-dqn]], [[cambc-replay-imitation]]) keyed on hp during the fight and was rejected; the data says hp at contact carries no signal, the power ratio does, and most losses open favourable and turn when reinforcements arrive.
**How to apply:** judge engagement by power ratio before contact, not hp mid-fight; don't retry hp cuts or first-contact power thresholds alone; the bigger lever is reinforcements (count enemies that can arrive) and converting favourable fights (hit first). Related: [[cambc-micro-tracking]] [[cambc-danger-level]] [[cambc-replay-imitation]] [[cambc-teammate-fixes3-cases]].
