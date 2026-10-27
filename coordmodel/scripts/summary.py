#!/usr/bin/env python3 -I
"""summary.py DEC.json.gz LABEL -> key numbers for both sides."""
import sys,gzip,json,collections
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
D=json.load(gzip.open(sys.argv[1])); lab=sys.argv[2]
R=D['rounds']; camps=D['camps']; st=D['meta']['stats']; final=D['meta']['final'] or R[-1]['r']
names={c['index']:c['typeName'] for c in st['champions']}; team={c['index']:c['team'] for c in st['champions']}
gtiles=collections.defaultdict(list); ginfo={}
for k in camps: gtiles[k[2]].append((k[3],k[4])); ginfo[k[2]]=(k[5],k[6])
r0=R[0]['c']; sp={}
for t in (0,1):
    pts=[(c[3],c[4]) for c in r0 if c[1]==t]; sp[t]=(sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
byr={row['r']:row for row in R}
print(f"## {lab}: {final} rounds, outcome {D['meta']['outcome']} (1=A,2=B), gems {D['meta']['gems']}, spawn dist {cheb(sp[0],sp[1])}")
totgems=sum(g for g,_ in ginfo.values()); 
print(f"groups: {len(ginfo)}, total gems on map {totgems}, gem groups {sum(1 for g,_ in ginfo.values() if g>0)}")
for side in (0,1):
    mine=[c[0] for c in r0 if c[1]==side]; own=sp[side]; en=sp[1-side]
    # per checkpoint
    cps=[150,300,550,800]
    line=[]
    for cp in cps:
        row=byr.get(min(cp,final))
        if not row: continue
        cs={c[0]:c for c in row['c']}
        gold=sum(cs[i][8] for i in mine); gems=sum(cs[i][7] for i in mine)
        line.append(f"r{cp}: gold-in-hand {gold} gems-in-hand {gems} banked {row['sg'][side]}")
    # earned gold by r300: use capgain
    earned={cp:0 for cp in cps}; spent={cp:0 for cp in cps}
    prev={}
    deaths=collections.Counter(); deaths300=0; pair=0; pn=0; alone=0; en_half=0; hn=0; enc=0
    firstcap=None; caps_by_side=[c for c in D['caps'] if c[1]==side]
    firstcap=caps_by_side[0][2] if caps_by_side else None
    gemcaps=sum(1 for g,t,r in caps_by_side if ginfo[g][0]>0)
    banks=[]; prevg={}
    shoptrips=collections.Counter(); first_shop={}
    for row in R:
        r=row['r']; cs={c[0]:c for c in row['c']}
        for i in mine:
            c=cs[i]
            if i in prev:
                p=prev[i]
                if c[9] and p[9]:
                    if c[8]>p[8] and c[7]>=p[7]:
                        for cp in cps:
                            if r<=cp: earned[cp]+=c[8]-p[8]
                    if c[8]<p[8] and cheb((c[3],c[4]),own)<=4:
                        for cp in cps:
                            if r<=cp: spent[cp]+=p[8]-c[8]
                        if r-shoptrips.get((i,'last'),-99)>3: shoptrips[i]+=1; first_shop.setdefault(i,r)
                        shoptrips[(i,'last')]=r
                    if c[7]<p[7]: banks.append(p[7]-c[7])
                if p[9] and not c[9]:
                    deaths[i]+=1
                    if r<=300: deaths300+=1
            prev[i]=c
            if c[9] and cheb((c[3],c[4]),own)>3:
                hn+=1
                md=min([cheb((c[3],c[4]),(cs[j][3],cs[j][4])) for j in mine if j!=i and cs[j][9]] or [99])
                if md<=4: pair+=1
                if md>6: alone+=1
                if cheb((c[3],c[4]),en)+5<cheb((c[3],c[4]),own): en_half+=1
                # enemy within 6
                if any(cheb((c[3],c[4]),(cs[j][3],cs[j][4]))<=6 for j in cs if team[j]!=side and cs[j][9]): enc+=1
    tn=[names[i] for i in mine]
    print(f"- side {side} ({'A' if side==0 else 'B'}) {', '.join(tn)}")
    print("  - "+"; ".join(line))
    print(f"  - capture gold earned by r150/300/550/800: {earned[150]}/{earned[300]}/{earned[550]}/{earned[800]}; spent at shop by r150/300/550/800: {spent[150]}/{spent[300]}/{spent[550]}/{spent[800]}")
    print(f"  - first capture r{firstcap}; captures total {len(caps_by_side)} (gem groups {gemcaps}); bank trips {len(banks)} mean {sum(banks)/max(1,len(banks)):.0f} gems")
    print(f"  - deaths total {sum(deaths.values())} (by r300: {deaths300}) per champ {dict((names[i],deaths[i]) for i in mine)}")
    print(f"  - off-spawn rounds {hn}: ally within 4 {100*pair/max(1,hn):.0f}%, no ally within 6 {100*alone/max(1,hn):.0f}%, in enemy half {100*en_half/max(1,hn):.0f}%, enemy within 6 {100*enc/max(1,hn):.0f}%")
    print(f"  - shop trips per champ {dict((names[i],shoptrips[i]) for i in mine)}, first shop round {dict((names[i],first_shop.get(i)) for i in mine)}")
