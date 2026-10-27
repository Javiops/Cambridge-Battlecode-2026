# o91 campexit (champ thread, 2026-10-25/27) - CLOSED

Mechanism (fb35dbg = b35 with one `[m]` mode line per round; 307/312 games byte-identical to b35):
- 90 of 660 local deaths r20-300 (14%) have no rival within 5 tiles. The camp kills us.
- When a group is already damaged ("engaged"), fight-camp skips the squad_needed admission. Example: boss_battle,
  where HoR and then Marcella each hit a 2 x 2400 hp elk group alone and lose 120 hp a round.
- x = time to clear / time to die, measured at the first fight-camp round:

  | x | dies | clears |
  |---|---|---|
  | < 0.5 | 1% | 70% |
  | 0.5-1 | 3% | 46% |
  | 1-2 | 7% | 30% |
  | 2-4 | 11% | 22% |
  | 4+ | 10% | 14% |

  Scripts: dseq.py, fcratio.py (champ scratch).

Piece `o91_campexit.py DIR X10 [HP]`: in fight-camp with the group engaged and no ally within 3 of its centre,
x is measured from my hp and the group hp over the last 2-4 rounds of this stay. If x >= X10/10 (and hp < HP%), drop
the group for 40 rounds and step home. It reads no fuel.

Local results, 312 games (26 near maps x 6 panel17 rivals x 2 sides) vs b35 (244 wins, 654 deaths r20-300).
Probe +20 on cx10: 0/52 games changed.

| variant | wins | + / - | deaths r20-300 |
|---|---|---|---|
| x>=1 | 183 | +16 / -77 | 686 |
| x>=2 | 199 | +15 / -60 | not measured |
| x>=2 and hp<50 | 224 | +15 / -35 | 618 |
| x>=4 and hp<40 | 234 | +11 / -21 | 631 |

Verdict: the strict variants cut deaths, but every variant loses wins. Camp time is worth more than the deaths it
costs, which matches the top-10 stats thread (27-10): the real gap is gems, 80 vs 38 at r150, not early deaths.
None of these goes to the PC.
