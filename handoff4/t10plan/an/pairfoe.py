# pairfoe.py: online v4b near maps: episodes where a pair (HoR+Vesper or Ryth+Marcella, both alive within 4) sees 3+ live rivals within 6;
# per episode: round, other pair's distance, and over the next 15 rounds: pair deaths, rivals killed nearby, action (fight / flee together / flee split)
import json,gzip,os,collections
W='/tmp/claude-0/w'
near=set(open('/tmp/claude-0/-home-user-cambridge-battlecode-2026/3dc070b2-a00b-5e31-ba97-59618d5276fa/scratchpad/near.txt').read().split())
T=[x for x in json.load(open(f'{W}/c34index.json')) if x['bot']=='t10plan4b' and x['map'] in near]
P=((12,1),(0,7)); EP=[]; G=0
ch=lambda a,b:max(abs(a[3]-b[3]),abs(a[4]-b[4]))
for x in T:
    D=json.load(gzip.open(f'{W}/dec/on4b/'+os.path.basename(x['file']).replace('.repl26a','.json.gz'))); us=0 if x['side']=='a' else 1; G+=1
    R=D['rounds']; last={0:-99,1:-99}
    for i,row in enumerate(R):
        r=row['r']
        if not 50<=r<600: continue
        cs={c[2]:c for c in row['c'] if c[1]==us}; en=[c for c in row['c'] if c[1]!=us and c[9]]
        for pi,(a,b) in enumerate(P):
            if a not in cs or b not in cs: continue
            A,B=cs[a],cs[b]
            if not (A[9] and B[9] and ch(A,B)<=4): continue
            ne=[e for e in en if min(ch(e,A),ch(e,B))<=6]
            if len(ne)<3: continue
            if r-last[pi]<=15: last[pi]=r; continue
            last[pi]=r
            oa,ob=P[1-pi]; od=min([ch(cs[k],q) for k in (oa,ob) if k in cs and cs[k][9] for q in (A,B)] or [99])
            # next 15 rounds
            dead=0; d0=min(ch(e,A) for e in ne); j=min(i+15,len(R)-1); fut={c[2]:c for c in R[j]['c'] if c[1]==us}
            for k in range(i+1,j+1):
                cc={c[2]:c for c in R[k]['c'] if c[1]==us}
                dead=sum(1 for t in (a,b) if t in cc and not cc[t][9])
            enj=[c for c in R[j]['c'] if c[1]!=us]; ekill=sum(1 for e in ne for f in enj if f[0]==e[0] and not f[9])
            FA,FB=fut.get(a),fut.get(b)
            if FA and FB and FA[9] and FB[9]:
                fd=min([ch(e,FA) for e in enj if e[9]] or [99])
                act='fight' if fd<=4 else ('flee-together' if ch(FA,FB)<=4 else 'flee-split')
            else: act='died'
            EP.append((r,od,dead,ekill,act,x['map']))
n=len(EP); print(f'{G} near games, {n} episodes ({n/G:.2f}/game); r151-300: {sum(1 for e in EP if 151<=e[0]<=300)/G:.2f}/game')
print('other pair <=10:', sum(1 for e in EP if e[1]<=10), ' 11-20:', sum(1 for e in EP if 10<e[1]<=20), ' >20 or dead:', sum(1 for e in EP if e[1]>20))
print('action:',collections.Counter(e[4] for e in EP)); print('pair deaths in 15r per episode %.2f, rivals killed %.2f'%(sum(e[2] for e in EP)/max(n,1),sum(e[3] for e in EP)/max(n,1)))
for k in ('<=10','>10'):
    s=[e for e in EP if (e[1]<=10)==(k=='<=10')]
    if s: print(f'other pair {k}: n {len(s)} deaths {sum(e[2] for e in s)/len(s):.2f} kills {sum(e[3] for e in s)/len(s):.2f}', collections.Counter(e[4] for e in s))
