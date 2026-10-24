# mgwp = v20c + monoguard-v1c + pairfarm pw3 + waitpair-v1 (bundle 0fd65cfa)

Base: mg1c+pw3 (v160). Added: waitpair-v1 (params P_WAITPAIR 1, P_WAITPAIR_D 12).
Mechanism: near maps (spawn path < 35), r30-150. While waiting for its camp to respawn, if an ally (seen, or estimated
from its claim) stands 3-12 tiles from the camp and the wait is >= distance+2, the champion waits next to that ally.
Log: `[pf] r150 <champ> ... walk N wp N` (wp = rounds waiting next to an ally).
Why: local diagnosis of r60-150 lonely rounds (pw3, 120 near games): approach 61% alone, capture 60%, wait-respawn 63%, fight-camp 29%.
Local near test (pw3 + waitpair, 120 games, 6 rivals): loneliness 43 -> 39%, gold r300 +266 -> +243, gems r300 +34 -> +26, fires 1.7 rounds/champion.
Hard panel vs v6d (480): net +1 (bar 23.7), far +6 mid +1 near -6; deaths -0.01, kills +0.10.
Judge online: loneliness (<=4) r60-150 near, paired-walk share, state r300-400; gold r300 must not drop.
