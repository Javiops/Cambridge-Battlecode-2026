# capby.py GLOB: captures r<400 per game attributed to our champions within 1 of a group tile at the capture round (by type)
import json,gzip,glob,sys,collections
N={1:'vesper',7:'marcella',12:'hor',0:'ryth',2:'vendetta'}
C=collections.Counter(); G=0
for f in glob.glob(sys.argv[1]):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f)); G+=1
    gt=collections.defaultdict(list)
    for k in D['camps']: gt[k[2]].append((k[3],k[4]))
    R={row['r']:row for row in D['rounds']}
    for g,t,r in D['caps']:
        if t!=us or r>=400 or r not in R: continue
        who=[c[2] for c in R[r]['c'] if c[1]==us and c[9] and min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in gt[g])<=1]
        for w in who: C[N.get(w,w)]+=1/len(who)
print(' '.join(f'{k} {v/G:.1f}' for k,v in sorted(C.items(),key=lambda x:-x[1])), f'({G})')
