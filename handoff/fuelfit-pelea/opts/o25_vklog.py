# fuelfit o25 (pelea): vesper.h's [vk] line was printed on every vkite hit (a printf is ~2500 fuel, on fight turns).
# It now prints only on rounds that are multiples of 100 (the counters are cumulative, so nothing is lost for the
# analyses that read the last line). Replays are unchanged; only stdout differs.
import sys
d=sys.argv[1]; p=d+'/vesper.h'; s=open(p,newline='').read()
a='                if (fuel_ok(30000)) std::printf("[vk] r%d %d/%d thr %d\\n", round, vk_hit, vk_dash, (int)thr);'
assert s.count(a)==1
s=s.replace(a,'                if (round % 100 == 0) std::printf("[vk] r%d %d/%d thr %d\\n", round, vk_hit, vk_dash, (int)thr);')
open(p,'w',newline='').write(s)
