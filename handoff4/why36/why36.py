# why36.py: c34 online losses (and wins) of v4o2/e1foco vs the 15 ahead: gem transfer on death, death context, rival packs in our half
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
def game(x):
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): return None
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; R=D['rounds']
    sp={t:[(c[3],c[4]) for c in R[0]['c'] if c[1]==t and c[3]>=0] for t in (0,1)}
    cen={t:(sum(p[0] for p in sp[t])/len(sp[t]),sum(p[1] for p in sp[t])/len(sp[t])) for t in (0,1)}
    def half(c):  # team whose spawn is nearer
        d0=(c[3]-cen[0][0])**2+(c[4]-cen[0][1])**2; d1=(c[3]-cen[1][0])**2+(c[4]-cen[1][1])**2
        return 0 if d0<d1 else 1
    o={t:collections.Counter() for t in (0,1)}
    prev={}; hist=collections.defaultdict(list)
    kc=D['kc']; cc=D['cc']
    for row in R:
        r=row['r']; cur={c[0]:c for c in row['c']}
        for c in row['c']:
            t=c[1]; p=prev.get(c[0])
            if c[9]: hist[c[0]].append((r,c[5],c[6]))
            if c[9] and r<=600: o[t]['carry']+=c[7]; o[t]['alive']+=1
            if p and p[9] and not c[9] and r<=600:
                ph='e' if r<=150 else ('m' if r<=300 else 'l')
                o[t]['d'+ph]+=1; o[t]['lost']+=p[7]; o[t]['lost'+ph]+=p[7]
                al=sum(1 for a in prev.values() if a[1]==t and a[0]!=c[0] and a[9] and ch(a,p)<=4)
                fo=sum(1 for a in prev.values() if a[1]!=t and a[9] and ch(a,p)<=5)
                o[t]['outn']+= fo>al+1
                o[t]['alone']+= al==0
                o[t]['ownhalf']+= half(p)==t
                # camp damage taken in the 15 rounds before death, and hp 15 rounds before
                ckd=sum(v for rr in range(r-15,r+1) for k,v in kc.get(str(rr),{}).items() if k.endswith('>'+str(c[0])))
                o[t]['campdmg15']+=ckd; o[t]['incamp']+= ckd>0
                h=[hp for rr,hp,mx in hist[c[0]] if rr<=r-15]
                if h: o[t]['hp15']+=h[-1]/p[6]; o[t]['hp15n']+=1
                ks=set(k.split('>')[0] for rr in range(r-5,r+1) for k in cc.get(str(rr),{}) if k.endswith('>'+str(c[0])))
                o[t]['killers']+=len(ks)
        # packs: >=3 champions of team t in the other half, all within 6 of one of them
        if 125<=r<=300:
            for t in (0,1):
                inv=[c for c in row['c'] if c[1]==t and c[9] and half(c)!=t]
                if any(sum(1 for b in inv if ch(a,b)<=6)>=3 for a in inv): o[t]['packr']+=1
        prev=cur
    for g,t,r in D['caps']:
        if r<=600 and t in (0,1): o[t]['caps']+=1
    sg=D['meta']['gems']
    return us,o,sg,D['meta']['outcome']
keys=['de','dm','dl','lost','loste','lostm','lostl','outn','alone','ownhalf','incamp','campdmg15','killers','packr','caps','carry','alive']
for bot in DIR:
    for res in ('loss','win'):
        S=[collections.Counter(),collections.Counter()]; n=0; hp=[0,0,0,0]; G=[0,0]
        for x in T:
            if x['bot']!=bot or x['result']!=res: continue
            g=game(x)
            if not g: continue
            us,o,sg,oc=g; n+=1
            for i,t in enumerate((us,1-us)):
                S[i].update(o[t]); G[i]+=sg[t]
        if not n: continue
        print(f'## {bot} {res} n={n}  (us / rival, per game)')
        print(f'  final gems {G[0]/n:.0f} / {G[1]/n:.0f}')
        for k in keys:
            print(f'  {k:10s} {S[0][k]/n:7.2f} / {S[1][k]/n:7.2f}')
        for i in (0,1):
            d=S[i]['de']+S[i]['dm']+S[i]['dl']
            print('  side',i,'per death: outnumbered %.2f alone %.2f ownhalf %.2f incamp %.2f hp15 %.2f killers %.2f gems lost %.1f'%(S[i]['outn']/d,S[i]['alone']/d,S[i]['ownhalf']/d,S[i]['incamp']/d,S[i]['hp15']/max(1,S[i]['hp15n']),S[i]['killers']/d,S[i]['lost']/d))
        print('  avg carried per alive champ-round: %.1f / %.1f'%(S[0]['carry']/S[0]['alive'],S[1]['carry']/S[1]['alive']))
