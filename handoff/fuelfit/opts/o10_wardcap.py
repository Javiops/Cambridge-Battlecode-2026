# fuelfit o10 (changes decisions a little): ward candidates per turn 12 -> 6. Each candidate is one SDK vision query
# plus two bitboard ops (~1.4k): the pass drops from ~17k worst to ~8k. Candidates are ordered dark-bush tiles first,
# so the best tile is usually among the first few. Judged by strength, not by fuel.
import sys
d=sys.argv[1]; p=d+'/params.h'; s=open(p,newline='').read()
a="#define P_WARD_TRY 12      // candidate tiles evaluated per turn (one vision query each)"
assert s.count(a)==1
s=s.replace(a,"#define P_WARD_TRY 6       // candidate tiles evaluated per turn (one vision query each); fuelfit o10: 12 -> 6")
open(p,'w',newline='').write(s)
