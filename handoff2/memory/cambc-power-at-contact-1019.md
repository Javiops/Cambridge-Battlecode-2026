---
name: cambc-power-at-contact-1019
description: 2026-10-19 after team-fight-v1: paired online diagnosis of v76, concentration study, shop-parity-v1 (v77) design + online REJECT and why (max hp is a correlate, not a lever); section-10 method rule
metadata:
  type: project
---
14:31 UTC online_diag_v76_1019.md (pinned v76-v72): 31-55 kills +1.33, deaths -1.43, kill8 18->24% (clear); 71-95 only kill8 +3.7 clear. Gems r250/r500 flat.
14:49 damage_focus_1019.md: concentration NOT the gap (both ~1.1 targets/round, 97% on top target). Same 3-round damage on hurt champ (ours 107-115, theirs 117-123) on less hp. Rivals put 33% of r300 shard gold in hp, v76 21%.
shop-parity-v1 (shop_parity_design_1019.md, Expected deaths -0.9 written before results): hp_pick share per type = rivals' r300 (Issac .28 Varg .31 Vendetta .29 Ryth .50 Ren .48 Tavi .20 Prism .28; 0.72x after r300). Container: deaths 4.3 vs 4.9, gems/monster dmg equal, h2h 71-83 (noise). maxhp_split_1019.md: gap +138, 89% hp shards/emblems, no level effect.
16:39 UTC ONLINE v77 REJECTED (audit verified judge_pinned.py shop-parity-v1-on-v76 76 77): 105 pairs, both 58-47, changed 12/12. 15:22 "resend" groups were v77 too (2nd unpinned batch, also 12/12). v76 stays base.
18:51 UTC WHY (online_mech_v77_1019.md): CASE (a): max hp at contact +82/champion (z 7.7), hurt start hp +34, s10 (d) -0.67, but deaths -0.08 (SE .59), kills +.31, wins 58-58, gems flat. Max hp is a CORRELATE, not a lever ("group indicator" grew +0.58).
METHOD RULE (audit 18:55 UTC): section-10 parts are bookkeeping; a part becomes a design target only with causal evidence (online paired change moving part AND outcome, like team-fight-v1 kill8/net kills on 31-55).
19:01 UTC score_margin_1019.md (225 v76 games 71-95): score sources = camp capture, kill moves victim bag, monster destroys bag, tribute (only score event). Deaths gap pooled +0.95 n.s.; it sits on killer rivals (ひななー, The World Machine, Sydney's Realist, test). Margin +99/game: wolf +111, kills +42, ELK -54 (behind r0-500, even in wins to r300). Losses: elk -170, mid -149 (mid follows result: +168 in wins). AUDIT 19:08: elk = lever candidate; asked choice/ability/contest per elk group, yield per champion-round elk vs wolf (stacking), elk gap vs killer vs farmer rivals, Expected in games flipped, same split on 10-18 top-30 replays. No design yet.
See [[cambc-team-fight-1019]], [[cambc-death-root-cause-1019]].
