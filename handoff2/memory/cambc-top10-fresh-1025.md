---
name: cambc-top10-fresh-1025
description: 10-25 thread "Comprobar si las stats del top 10 están anticuadas": top10 turnover + draft shift (Tavi 14->46%, Ryth 56->29%) since 10-23; public-API collector; same-script recompute of reference stats on fresh games
metadata:
  type: project
  modified: 2026-10-25T12:19:38.739Z
---
Thread cmsg_017gbamt2g1g8hMHRHQBc6qbVoK5gm5dbDsc5ynjLYzo5q (user 10-25 12:07 UTC: "a ver si estamos persiguiendo stats anticuados... necesito que lo hagas mejor").
- PUBLIC API (no cookie) gives match lists + drafts + scores: /match-groups?scope=all&team=ID (paginate with p['next'], NOT createdAt), /match-groups/ID. Summaries and bundles need the cookie (401) -> ask coordinator -> loop.
- 10-25 ~12:30 UTC findings (≈9k top10 games since 10-24 18:00): top10 turned over (Claudus #2, Mite, willow, hello up; Pantheon/procless/Sponge/new team(4) out). t10-vs-t10 picks: Tavi 14->46%, Vendetta 60->80%, Ryth 56->29% (WR 42%), Prism 32->11%; top draft hor+marcella+tavi+vendetta+vesper. Teams kept their own drafts (shift = who is top + Claudus volume). Repeated same pairing+map differs 70-84% after >30 min -> bots change every few hours. Unchanged: game length per map, t10 WR vs ranks 30-60 (87-88%).
- Files: /mnt/project-files/analysis/top10-fresh-1025/ (sel_1025.json, ids_band_1025.txt, ids_t10_1025.txt; summaries/replays requested from loop). Scripts (copy to that folder when done): summ.py (stats JSON), rmet.py (r300 dumps: first capture, elk by r50, deaths, trios r30-90, fight numbers), draft2.py, det.py.
- rmet.py on old dec300 reproduces refs: elk r50 0.62, deaths<=100 0.35, first3 3+ 51%, trios 40%; its +2 definition gives 8% (not the 36-43% of the pelea audit) -> compare relative only.
Related: [[cambc-top10-micro-1023]] [[cambc-top10-plan-1024]] [[cambc-farm-throughput-1025]]
