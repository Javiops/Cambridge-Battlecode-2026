import json,sys,collections
d=json.load(open(sys.argv[1]));T=d['T'];G=d['games'];print('games',G)
A=collections.defaultdict(collections.Counter)
for k,v in T.items():
    lab,t,cls,m=k.split('|')
    if cls=='ALL': A[(lab,t,'ALL')][m]+=v; A[(lab,'ALL','ALL')][m]+=v; continue
    for tt in (t,'ALL'):
        for cc in (cls,'any'): A[(lab,tt,cc)][m]+=v
for t in ['ALL','Marcella','HeartOfRuin','VesperVale','Ryth','Vendetta','Ren','Tavi','Prism','Stellar','Cassi','Issac','Varg','Willow']:
    rows=[]
    for cls in ['even','down','up']:
        s=[]
        for lab in ['us','them']:
            c=A[(lab,t,cls)]; n=c['ep']
            s.append(f"{lab}: ep/g {n/G:4.2f} kill {c['kills']/max(1,n):.2f} dead {c['dead']/max(1,n):.2f} hurt->dead {c['hurtdead']/max(1,c['hurt']):.2f}")
        rows.append(f'{t:11s} {cls:5s} '+' | '.join(s))
    if all(A[(lab,t,'any')]['ep']==0 for lab in ['us','them']): continue
    print('\n'.join(rows))
    dd={lab:A[(lab,t,'any')] for lab in ['us','them']}
    print(f"{t:11s} deaths/g us {dd['us']['dead']/G:.2f} (down {A[('us',t,'down')]['dead']/G:.2f}) them {dd['them']['dead']/G:.2f} (down {A[('them',t,'down')]['dead']/G:.2f}); after-leave us {A[('us',t,'ALL')]['after_dead']/G:.2f} them {A[('them',t,'ALL')]['after_dead']/G:.2f}")
