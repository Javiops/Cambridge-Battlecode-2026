# tlsum.py LABEL PREFIX...: per game ally<=4 off spawn r50-600, deaths r0-150/150-300/300-600, team captures per span, win
import json,gzip,sys,subprocess,re
maps=['crossing','contest','elk_arena','stampede','gemfight','vault']
def one(pre,m,sd):
    f=f'/tmp/claude-0/w/tl/{pre}_{m}_{sd}.json.gz'; us=0 if sd=='a' else 1
    D=json.load(gzip.open(f)); c0=D['rounds'][0]['c']; sp=[(c[3],c[4]) for c in c0 if c[1]==us]
    a=n=0; dd=[0,0,0]; prev={}
    for row in D['rounds']:
        r=row['r']; A=[c for c in row['c'] if c[1]==us and c[9]]
        for c in row['c']:
            if c[1]==us:
                if prev.get(c[0],1) and not c[9] and r<600: dd[0 if r<150 else 1 if r<300 else 2]+=1
                prev[c[0]]=c[9]
        if r<50 or r>=600: continue
        for c in A:
            if min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in sp)<=4: continue
            n+=1; a+=any(e is not c and max(abs(c[3]-e[3]),abs(c[4]-e[4]))<=4 for e in A)
    out=subprocess.run(['python3','/tmp/claude-0/w/coord/timeline.py',f,str(us),pre],capture_output=True,text=True).stdout
    caps=[0,0,0]
    for L in out.splitlines():
        mm=re.match(r'\| (\d+)-\d+ \|.*caps (\d+)',L)
        if mm:
            r0=int(mm.group(1))
            if r0<600: caps[0 if r0<150 else 1 if r0<300 else 2]+=int(mm.group(2))
    hd=re.search(r'rounds (\d+), result (-?\d+)',out); win=('W' if int(hd.group(2))==us else 'L')+' '+hd.group(1)
    return a/max(n,1),dd,caps,win,out
print(f'| map side | {sys.argv[1]} ally | deaths | caps | win |'); print('|---|---|---|---|---|')
tot=[0,0,0]; full=[]
for m in maps:
    for sd in 'ab':
        al,dd,cp,w,out=one(sys.argv[2],m,sd); full.append(f'## {m} {sd}\n'+out)
        print(f'| {m} {sd} | {al:.0%} | {"/".join(map(str,dd))} | {"/".join(map(str,cp))} | {w} |')
        tot[0]+=al; tot[1]+=sum(dd); tot[2]+=w[0]=='W'
print(f'\n{sys.argv[1]}: mean ally {tot[0]/12:.0%}, deaths r0-600 {tot[1]/12:.1f}/game, wins {tot[2]}/12')
open(f'/tmp/claude-0/w/tl/timelines_{sys.argv[2]}.md','w').write('\n\n'.join(full))
