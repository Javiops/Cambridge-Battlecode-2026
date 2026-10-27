#!/usr/bin/env python3 -I
"""timeline.py DEC.json.gz SIDE(0/1) LABEL -> per-50-round timeline of SIDE's champions (markdown)."""
import sys, gzip, json, collections
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def main(path, side, label, win=50):
    D=json.load(gzip.open(path)); R=D['rounds']; camps=D['camps']; st=D['meta']['stats']
    names={c['index']:c['typeName'] for c in st['champions']}
    team={c['index']:c['team'] for c in st['champions']}
    # group geometry
    gtiles=collections.defaultdict(list); ginfo={}
    for k in camps:
        idx,typ,g,sx,sy,gg,gd,mhp,rd=k
        gtiles[g].append((sx,sy)); ginfo[g]=(gg,gd)
    gcent={g:(sum(x for x,_ in t)/len(t),sum(y for _,y in t)/len(t)) for g,t in gtiles.items()}
    r0=R[0]['c']
    sp={}
    for t in (0,1):
        pts=[(c[3],c[4]) for c in r0 if c[1]==t]
        sp[t]=(sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
    own=sp[side]; en=sp[1-side]
    mine=[c[0] for c in r0 if c[1]==side]
    final=D['meta']['final'] or R[-1]['r']
    # events
    caps=D['caps']  # [group, team, round]
    cap_by_r=collections.defaultdict(list)
    for g,t,r in caps:
        if t==side: cap_by_r[r].append(g)
    deaths=collections.defaultdict(list)  # round -> champion idx died
    prev_alive={}; prev_gems={}; prev_gold={}
    bank=collections.defaultdict(list); shop=collections.defaultdict(list); capgain=collections.defaultdict(list)
    kills=collections.defaultdict(list)  # round -> (killer, victim)
    cc=D['cc']
    byr={}
    for row in R:
        r=row['r']; byr[r]=row
        for c in row['c']:
            i=c[0]; alive=c[9]
            if i in prev_alive and prev_alive[i] and not alive:
                deaths[r].append(i)
                # credit: attackers in last 3 rounds
                att=set()
                for rr in range(r-3,r+1):
                    for key,v in cc.get(str(rr),{}).items():
                        a,b=key.split('>')
                        if int(b)==i: att.add(int(a))
                for a in att: kills[r].append((a,i))
            if i in prev_gems and alive and prev_alive.get(i):
                if c[7]<prev_gems[i]: bank[r].append((i,prev_gems[i]-c[7]))
                if c[8]<prev_gold[i] and cheb((c[3],c[4]),sp[team[i]])<=4: shop[r].append((i,prev_gold[i]-c[8]))
                if c[8]>prev_gold[i] and c[7]>=prev_gems[i]: capgain[r].append((i,c[8]-prev_gold[i],c[7]-prev_gems[i]))
            prev_alive[i]=alive; prev_gems[i]=c[7]; prev_gold[i]=c[8]
    out=[]
    out.append(f"### {label}: rounds {final}, result {D['meta']['outcome']} gems {D['meta']['gems']}")
    out.append("side champions: "+", ".join(f"{i}:{names[i]}" for i in mine))
    tot=collections.OrderedDict()
    for c in st['champions']:
        if c['team']==side: tot[c['index']]=c
    out.append("totals: "+"; ".join(f"{names[i]} K{c['kills']}/D{c['deaths']}/A{c['assists']} gold {c['earnedGold']} gems {c['collectedGems']} dmgC {int(c['championDamageDone'])} dmgM {int(c['monsterDamageDone'])}" for i,c in tot.items()))
    gl=sorted(ginfo.items()); 
    out.append("groups (gems/gold per GROUP, centre, half): "+", ".join(f"G{g}={gg}g/{gd}au@({gcent[g][0]:.0f},{gcent[g][1]:.0f}){'o' if cheb(gcent[g],own)+4<cheb(gcent[g],en) else 'e' if cheb(gcent[g],en)+4<cheb(gcent[g],own) else 'm'}" for g,(gg,gd) in gl if gg+gd>0))
    out.append("")
    out.append("| rounds | "+" | ".join(names[i][:6] for i in mine)+" | team |")
    out.append("|---|"+"---|"*len(mine)+"---|")
    for w0 in range(0, final+1, win):
        w1=min(w0+win-1, final)
        cells=[]
        team_caps=[]; team_bank=0; team_shop=0
        for r in range(w0,w1+1):
            for g in cap_by_r.get(r,[]): team_caps.append(g)
        for i in mine:
            pos=collections.Counter(); hp=[]; ad=[]; alone=0; n=0; dead=0; gl_=[]
            for r in range(w0,w1+1):
                row=byr.get(r)
                if not row: continue
                cs={c[0]:c for c in row['c']}
                c=cs[i]
                if not c[9]: dead+=1; continue
                n+=1; p=(c[3],c[4]); hp.append(c[5]/max(1,c[6]))
                # position class
                lab=None
                if cheb(p,own)<=3: lab='H'
                else:
                    bg=None;bd=99
                    for g,t in gtiles.items():
                        d=min(cheb(p,q) for q in t)
                        if d<bd: bd=d;bg=g
                    if bd<=3: lab=f"G{bg}"
                    else:
                        do=cheb(p,own); de=cheb(p,en)
                        lab='own' if do+5<de else 'en' if de+5<do else 'mid'
                pos[lab]+=1
                md=99
                for j in mine:
                    if j==i: continue
                    cj=cs[j]
                    if cj[9]: md=min(md,cheb(p,(cj[3],cj[4])))
                if md<99: ad.append(md)
                if md>4: alone+=1
            if n==0:
                cells.append("dead"); continue
            top=pos.most_common(2)
            poss="/".join(f"{l}{int(100*k/n)}" for l,k in top)
            mh=sum(hp)/len(hp)
            hb='hp<30' if mh<0.3 else 'hp30-60' if mh<0.6 else 'hp60-90' if mh<0.9 else 'hp90+'
            mad=sum(ad)/len(ad) if ad else 99
            mycaps=[]
            for r in range(w0,w1+1):
                for g in cap_by_r.get(r,[]):
                    row=byr.get(r); 
                    if not row: continue
                    c=[x for x in row['c'] if x[0]==i][0]
                    if c[9] and min(cheb((c[3],c[4]),q) for q in gtiles[g])<=1: mycaps.append(g)
            k=sum(1 for r in range(w0,w1+1) for a,v in kills.get(r,[]) if a==i)
            d=sum(1 for r in range(w0,w1+1) for v in deaths.get(r,[]) if v==i)
            b=sum(v for r in range(w0,w1+1) for a,v in bank.get(r,[]) if a==i)
            sh=sum(v for r in range(w0,w1+1) for a,v in shop.get(r,[]) if a==i)
            cg=sum(v for r in range(w0,w1+1) for a,v,_ in capgain.get(r,[]) if a==i)
            s=f"{poss} a{mad:.0f}({int(100*alone/n)}%) {hb}"
            if mycaps: s+=" cap:"+",".join(f"G{g}" for g in mycaps)
            if cg: s+=f" +{cg}au"
            if b: s+=f" bank{b}"
            if sh: s+=f" shop{sh}"
            if k or d: s+=f" K{k}D{d}"
            if dead: s+=f" dead{int(100*dead/(n+dead))}%"
            cells.append(s)
        # team cell
        sgs=byr.get(w1,byr.get(max(byr)))['sg'][side]
        tc=collections.Counter(team_caps)
        cells.append(f"caps {len(team_caps)} "+",".join(f"G{g}x{k}" if k>1 else f"G{g}" for g,k in sorted(tc.items()))+f" banked={sgs}")
        out.append(f"| {w0}-{w1} | "+" | ".join(cells)+" |")
    print("\n".join(out))
if __name__=='__main__':
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
