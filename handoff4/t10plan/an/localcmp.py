import sys,glob,os
sys.path.insert(0,'/tmp/claude-0/w/an')
from feat import feats
from agg import team_bin
from collections import defaultdict
d=sys.argv[1]
S={0:defaultdict(float),1:defaultdict(float)}; n=defaultdict(int)
for f in glob.glob(f'/tmp/claude-0/w/dec/{d}/*.json.gz'):
    F=feats(f, rmax=700); us=0 if os.path.basename(f).split('.')[0].endswith('_a') else 1
    for b in range(1,7):
        for who,t in ((0,us),(1,1-us)):
            o=team_bin({'F':F,'team':t},b)
            if not o: continue
            n[who]+=1
            for k,v in o.items(): S[who][k]+=v
for k in ('alive','deaths','fr','own','al4','big','contact','outn','h_mates','caps','capgems','hitr'):
    print(f'{k:8} cand {S[0][k]/n[0]:6.2f}  opp {S[1][k]/n[1]:6.2f}')
