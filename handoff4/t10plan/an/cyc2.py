# cyc.py GLOB: carry capture rate r0-400 = captures / rounds on a camp (within 2 of a camp tile) + escort rounds within 2 of the carry's camp tiles
import os
WIN=os.environ.get('WIN')
import json,gzip,glob,sys,collections
caps=0; camp=0; help_=0; n=0
for f in glob.glob(sys.argv[1]):
    D=json.load(gzip.open(f)); us=(0 if f.endswith('_a.json.gz') else 1) if not WIN else D['meta']['outcome']-1
    if us not in (0,1): continue
    gt=collections.defaultdict(list)
    for k in D['camps']: gt[k[2]].append((k[3],k[4]))
    tiles=[t for v in gt.values() for t in v]
    R={row['r']:row for row in D['rounds']}
    for g,t,r in D['caps']:
        if t!=us or r>=400 or r not in R: continue
        if any(c[2] in (1,7) and c[9] and min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in gt[g])<=1 for c in R[r]['c'] if c[1]==us): caps+=1
    for row in D['rounds']:
        if row['r']>=400: break
        cs=[c for c in row['c'] if c[1]==us and c[9]]
        for c in cs:
            if c[2] not in (1,7): continue
            near=[t for t in tiles if max(abs(c[3]-t[0]),abs(c[4]-t[1]))<=2]
            if not near: continue
            camp+=1
            help_+=any(e[2] not in (1,7) and max(abs(c[3]-e[3]),abs(c[4]-e[4]))<=3 for e in cs)
    n+=1
print(f'carry captures/game {caps/n:.1f}, carry camp-rounds/game {camp/n:.0f}, rounds per capture {camp/max(caps,1):.0f}, camp-rounds with an escort <=3 {help_/max(camp,1):.0%}')
