# v7chk.py: v7 vs v4o2 local (both vs kvvl): per game first v7 firing (stdout), first divergence round, deaths with 3+ foes within 6 (ours, r151-600), result
import json,gzip,os,zipfile,re,sys,collections
W='/tmp/claude-0/w'
A,B=sys.argv[1],sys.argv[2]   # rep tags: candidate, base
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
def load(tag,f): return json.load(gzip.open(f'{W}/dec/{tag}/{f}.json.gz'))
def stats(D,us):
    prev={}; d3=0; d=0; caps=0
    gv={}
    for k in D['camps']: gv[k[2]]=max(gv.get(k[2],0),k[5] or 0)
    big=sum(1 for g,t,r in D['caps'] if t==us and r<=600 and gv.get(g,0)>=40)
    for row in D['rounds']:
        r=row['r']
        for c in row['c']:
            p=prev.get(c[0])
            if p and p[9] and not c[9] and c[1]==us and 150<r<=600:
                d+=1
                if sum(1 for a in prev.values() if a[1]!=us and a[9] and ch(a,p)<=6)>=3: d3+=1
        prev={c[0]:c for c in row['c']}
    return d,d3,big
S=collections.Counter(); ident=0; n=0; early=0
for fn in sorted(os.listdir(f'{W}/ws/rep/{A}')):
    if not fn.endswith('.repl26a'): continue
    b=fn[:-8]; side=b[-1]; us=0 if side=='a' else 1
    z=zipfile.ZipFile(f'{W}/ws/rep/{A}/{fn}')
    out=z.read(f'team-{side}.stdout').decode(errors='replace')
    rr=[int(m.group(2)) for m in re.finditer(r'\[v7-(rejudge|join)\] r=(\d+)',out)]
    S['rj']+=out.count('[v7-rejudge]'); S['jn']+=out.count('[v7-join]')
    first=min(rr) if rr else 10**9
    try: Da=load(A,b); Db=load(B,b)
    except Exception as e: continue
    n+=1
    div=None
    for x,y in zip(Da['rounds'],Db['rounds']):
        if x['c']!=y['c']: div=x['r']; break
    if div is None and len(Da['rounds'])==len(Db['rounds']): ident+=1
    elif div is not None and div<first-1: early+=1; print('EARLY divergence',b,'div',div,'first firing',first)
    for tag,D,k in ((A,Da,'a'),(B,Db,'b')):
        d,d3,big=stats(D,us); S[k+'d']+=d; S[k+'d3']+=d3; S[k+'big']+=big
        S[k+'win']+= D['meta']['outcome']==us+1
print(f'games {n}: identical {ident}, diverged before the first firing {early}; firings rejudge {S["rj"]/n:.2f}/game join {S["jn"]/n:.2f}/game')
print(f'{A} vs {B}: wins {S["awin"]}/{S["bwin"]}; deaths r151-600 {S["ad"]/n:.2f}/{S["bd"]/n:.2f}; with 3+ foes {S["ad3"]/n:.2f}/{S["bd3"]/n:.2f}; 40+ captures r<=600 {S["abig"]/n:.2f}/{S["bbig"]/n:.2f}')
