---
name: cambc-archive-mac-1023
description: Where archived replays/camstat/summaries/old analysis went (Windows PC C:\Users\Javier\Cambc2026\archive, via repo Javiops/cambc-archive) and how threads read them back
metadata:
  type: reference
  modified: 2026-10-24T14:39:00.263Z
---
Thread "Archivo de repeticiones en el PC" cmsg_017gbamt2g1g8hMHRHQBc6qbTQhdiKjnePxZstAedQiJd9. Index: /mnt/project-files/archive/MANIFEST.md.
- 10-23 22:30 UTC: 11,468 files (camstat+summaries <10-23, replays_old_le131.zip, analysis/claude-api-2026-10-18/data, new-maps-2026-10-16, analysis/replays, v53-replay-review) moved to the Mac /Users/javier/Downloads/bot2_osc_dash_survival_v1/cambc-archive/.
- 10-24 14:45 UTC: FINAL home = Windows PC C:\Users\Javier\Cambc2026\archive\ (old2/, sum2/, mac/ + README.txt), all sha256+CRC verified. old2 = top50_1022, top10-patch-1020, top10-balance-patch-1021, ga-farm, top5_study_compact, v35-dissection, replay-dataset, cambc-3.0.4 wheel (1,892); sum2 = summaries+camstat <10-23 12:00 (3,982); mac = copy of the Mac archive. Project folder ~7.9 GB after.
How it works: thread device link reaches only the Mac; Windows only via Remote Control (start_remote_control, folder C:\Users\Javier\Cambc2026), which can't see /mnt/project-files. Bridge = private repo Javiops/cambc-archive (user created it with gh; sessions get 403 creating repos; add_repo push works; files <100 MB). PC session: gh signed in as Javiops, no Python, core.autocrlf=true (text checksums can break), 145 GB free.
Kept in project (in use): top10_1022, chains, replays, groups, bot/, bundles/, local-filter-1021.
