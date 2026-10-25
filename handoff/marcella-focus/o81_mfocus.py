# o81 mfocus (marcella.h shop_plan): Marcella buys spell power. Why (10-25): her 2 x Focus spell hits 120 in every
# phase for us (no Focus bought: 0.0 Focus shards at r200, 0.2 at r300), the top 10's 123 / 163 / 255 in r30-100 /
# r100-200 / r200-300; they split shards about equally (r300: strength 4.7, health 5.6, focus 5.1 of 13.5), we buy
# health (4.8 of 6.6). P_MSHOP 1: Treasure-f instead of Treasure-h (same price and passive, +10 focus a shard instead of
# +100 hp); 2: also the two Bruiser-f before the two Bruiser-h; 3: Treasure-s (strength) for comparison.
import sys
d=sys.argv[1]; v=int(sys.argv[2]) if len(sys.argv)>2 else 1
def edit(fn, pairs):
    p=d+'/'+fn; s=open(p,newline='').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:60],s.count(a)); s=s.replace(a,b)
    open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read(); nl='\r\n' if '\r\n' in s else '\n'
s=s.rstrip('\r\n')+nl+nl.join(["","// o81 mfocus (marcella.h shop_plan): 0 = t10shop-v1 plan; 1 Treasure-f; 2 Treasure-f + Bruiser-f first; 3 Treasure-s",
"#ifndef P_MSHOP","#define P_MSHOP %d"%v,"#endif"])+nl
open(p,'w',newline='').write(s)
edit('marcella.h',[("""    s.plan = {{"treasure", 'h', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 2}, {"durab", 'h', 1}, {"bruiser", 'f', 2}, {"bruiser", 'h', 99}};""",
"""#if P_MSHOP == 1  // o81: spell power (top 10: 2 x Focus spell 163 at r100-200, 255 at r200-300; ours 120)
    s.plan = {{"treasure", 'f', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 2}, {"durab", 'h', 1}, {"bruiser", 'f', 2}, {"bruiser", 'h', 99}};
#elif P_MSHOP == 2
    s.plan = {{"treasure", 'f', 1}, {"jungle", 's', 1}, {"bruiser", 'f', 2}, {"bruiser", 'h', 2}, {"durab", 'h', 1}, {"bruiser", 'h', 99}};
#elif P_MSHOP == 3
    s.plan = {{"treasure", 's', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 2}, {"durab", 'h', 1}, {"bruiser", 'f', 2}, {"bruiser", 'h', 99}};
#else
    s.plan = {{"treasure", 'h', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 2}, {"durab", 'h', 1}, {"bruiser", 'f', 2}, {"bruiser", 'h', 99}};
#endif""")])
