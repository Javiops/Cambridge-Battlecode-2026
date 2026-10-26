---
name: cambc-chain-tools-1024
description: Online chain judging tools (pair_exact dedup, near/far split, a14 state model r300-600), chain index paths, and 10-24 outcomes (vco closed +14/500)
metadata:
  type: project
  modified: 2026-10-24T08:48:48.429Z
---
Loop thread [[cambc-online-loop]] judges each chain candidate on the same pinned groups as its base draw.
- games.jsonl has duplicate rows: always dedup by match id before pairing (pair_exact.py counted 205 games for one 125-game batch on 10-24).
- Chain data: online/data/chain{N}_10xx/index.json + analysis/chain{N}-10xx/summaries (chains 3-4 dated 1023, 5+ dated 1024). Each chain's downloader must get an UNTIL bound when the next base starts, else the next base is indexed as 'base'.
- Since 10-24 08:41 (user-approved via stall thread): verdicts also report state at r300/400/600: `python3 -I analysis/stall-1024/build.py OUT.json chain3_1023 chain4_1023 chain5_1024 ...` (ALWAYS all chains from 3; model fits on all V20 games) then `python3 -I a14.py OUT.json` (~3 min) -> expected net wins by state ± 2se next to real net.
- Focus moved 10-24 to the first 150 rounds on near maps; late pieces paused. Top-10-vs-band data: online/data/t10_vs_band_1024/ (index.json, summaries, t10_near_40.json, v20_near_80.json).
- 10-24 night results (all on V20 base, none passed): vkite +6/370, fo2r 0, vk-ls -6, lshop-v1c -3, vgold-far-c +1, vcarry-open (vco) +14/500 over 4 draws (closed; gem gain not stable), pack vk+vco+ls +6.
- /submissions lists only the newest 20 versions (more=true); older ids need `/submissions?before=<lowest version shown>`. Activating V20 (v139, id 08057430-fcae-406e-8880-d461c79bcadd) by m[139] from page 1 broke 10-24 11:41; loop uses scratch act.py V (paginates).
- 10-24 13:20 lost 20 min of full quota: loop waited for candidates without queuing the next base. Rule: when a chain's last send finishes, ALWAYS queue the next V20 base draw at once.
- 10-24 15:47 UTC chain 14 bug (user spotted "2 games al mismo bot"): an old chain14.sh survived a kill+relaunch, two base draws sent the same draw in lockstep -> 12 rivals got their group twice. Rule: launch chains as `nohup flock -n X.lock bash chainN.sh`, base_draw under flock draw.lock (template chain6.sh), and check `ps` for one instance after every relaunch.
- 10-24 18:30 UTC: ONLINE GAMES ARE DETERMINISTIC: 60/60 duplicate V20 games (same rival/map/side) identical in result, gems, rounds. Every changed pair = code (or rival bot) difference, not chance. The 'kall' v163 was really kvvl code (see upload bug), so c14/c15 'kall' results are kvvl results.
- 10-24 16:42 UPLOAD BUG: kvvl submit returned 'invalid response' but landed late, at the same ms as kall's: v162=kall got 'cancelled', v163=kvvl labelled kall. multi_cand.sh now accepts only a new non-cancelled version whose size equals a local `cambc bundle`. After each upload grep the piece's counter in the first game's team-*.stdout (replay zip).
- 10-24 site: a new upload becomes ACTIVE by itself once compiled (v169 21:2x UTC), and switching active while a version compiles CANCELS it (v165). Activation takes up to ~10 min to show in /submissions active. act.py waits for active only (<=15 min). With kvvl on ranked, re-activate 164 after every upload compiles.
