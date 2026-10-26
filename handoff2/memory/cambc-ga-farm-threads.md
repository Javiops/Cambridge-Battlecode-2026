---
name: cambc-ga-farm-threads
description: 2026-10-16 thread ids of the GA farm: farm/tooling thread, 7 cloud islands a-g (seeds, scopes), PC island, DQN track, micro/structure/macro threads
metadata:
  type: project
---

Thread ids for [[cambc-ga-farm]] (one thread per island).
- Farm "GA farm: islands on cloud and PC" (branch claude/ga-farm, cmsg_017gbamt2g1g8hMHRHQBc6qbDLwfHubcut12sLkzi16aS3): unified tools/ga from PR #19 (weights) + PR #22 (structure); runs cloud-a (micro+structure+gp first) and `island.py champion` every 2 h.
- cloud-b micro seed 1002 cmsg_017gbamt2g1g8hMHRHQBc6qbCokBEYoYQFpvSmDh1cJfok
- cloud-c micro 1003 cmsg_017gbamt2g1g8hMHRHQBc6qb7nMmpwUFdBR7aXogjvrNF5
- cloud-d structure 1004 cmsg_017gbamt2g1g8hMHRHQBc6qb4ssxLPn4xuSUWfsbiYwR4h
- cloud-e gp 1005 cmsg_017gbamt2g1g8hMHRHQBc6qb2WyDFB1xHsHSNShi4qVrQw
- cloud-f neat 1006 cmsg_017gbamt2g1g8hMHRHQBc6qb3x4LR6Kyk99bz7AqFrnAqf
- cloud-g all 1007 cmsg_017gbamt2g1g8hMHRHQBc6qb3oKHrEBT6e4g8SpxhFTFqn
- PC island "PC island for the GA" cmsg_017gbamt2g1g8hMHRHQBc6qbV8MYW4MU44w9Lcf75xE4wD (Remote Control, C:\Users\Javier\Cambc2026, cambc 2.2.1).
- "Algoritmo genético para la micro" = weights island (v44, PR #19); "Evolucionar la estructura de la micro" = structure island (L1 on v44, GP L2, NEAT L3, PR #22); "GA macro: economy genes" (claude/ga-macro) = 49-gene economy GA on main + v44 params (stacking, recalls, gold pickup, chaining, shop, map-feature thresholds; checkpoint ga-farm/islands/macro/, restore.sh, 15-min self check-in); "Acelerar las partidas y el desarrollo" measured the PC. Only "Dissect the top 2 teams" sends online challenges (150 games/h).
- 11:45 DQN track cmsg_017gbamt2g1g8hMHRHQBc6qbAtqtPcREAqYViqgM2BaGCn, outputs /mnt/project-files/analysis/dqn-2026-10-16/, builds on [[cambc-rl-assessment]].
