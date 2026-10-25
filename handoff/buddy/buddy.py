# buddy.py LIST: r30-300 distance between roster slots (0,1),(2,3),(3,4) when both alive (median and <=3 share)
import json,sys,collections,statistics
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
L=json.load(open(sys.argv[1])); D=collections.defaultdict(list)
for fn,us in L:
    for l in open(fn):
        try: d=json.loads(l)
        except: continue
        r=d['round']
        if not 30<=r<300: continue
        M=[c for c in d['champions'] if c['team']==us and c['typeName']!='Issac']
        M.sort(key=lambda c:c['index'])
        for a,b in ((0,1),(2,3),(3,4),(0,2),(1,3)):
            if b<len(M) and M[a]['alive'] and M[b]['alive'] and M[a]['x']>=0 and M[b]['x']>=0:
                D[(a,b)].append(ch((M[a]['x'],M[a]['y']),(M[b]['x'],M[b]['y'])))
print(sys.argv[1],' '.join(f'{k}: med {statistics.median(v):.0f} le3 {sum(x<=3 for x in v)/len(v):.0%}' for k,v in D.items()))
