# fpt_agg.py RESDIR [THR]: heavy farm turns ([fpt] lines with section 11 >= THR) : what the scopes cost on them
import zipfile,glob,sys,collections,re,statistics as st
names={0:'pre',1:'init',2:'shop',3:'vision',4:'groups',5:'foes',6:'camps',7:'support',8:'decide',9:'fight',10:'recall',11:'FARM',12:'post',13:'log',15:'choose_target',16:'step_towards',17:'engage',18:'best_altar',19:'br_altar_dist',20:'go_tribute',24:'other_captures',26:'evac',30:'engage_camp',31:'refresh_groups',32:'near_camps',33:'farm()',34:'my_dps',35:'allies_near'}
THR=float(sys.argv[2]) if len(sys.argv)>2 else 25000
rows=[]; games=0
for f in glob.glob(sys.argv[1]+'/*/*.repl26a')+glob.glob(sys.argv[1]+'/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    try: t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    except KeyError: continue
    games+=1
    for l in t:
        if '[fpt]' not in l: continue
        p=l[l.index('[fpt]')+5:].split(); d={'r':int(p[0][1:]),'who':p[1],'tot':float(p[2].split('=')[1])}
        for kv in p[3:]:
            k,v=kv.split('='); d[int(k)]=float(v)
        rows.append(d)
H=[d for d in rows if d.get(11,0)>=THR]
print(f'games {games}; [fpt] turns {len(rows)}; farm>={THR:.0f}: {len(H)} ({len(H)/games:.1f}/game)')
if H:
    print('farm section on those turns: median %.0f p90 %.0f max %.0f'%(st.median(d[11] for d in H), sorted(d[11] for d in H)[int(0.9*len(H))], max(d[11] for d in H)))
    print('round dist: r<=5 %d, r6-50 %d, r51-300 %d, r>300 %d'%(sum(1 for d in H if d['r']<=5),sum(1 for d in H if 5<d['r']<=50),sum(1 for d in H if 50<d['r']<=300),sum(1 for d in H if d['r']>300)))
    print(f"{'scope':16}{'mean':>8}{'present%':>9}{'mean|present':>13}{'max':>8}")
    for k in sorted(names):
        v=[d.get(k,0) for d in H]; pres=[x for x in v if x>0]
        if not pres: continue
        print(f"{names[k]:16}{st.mean(v):8.0f}{100*len(pres)/len(H):8.0f}%{st.mean(pres):13.0f}{max(v):8.0f}")
    # dominant scope per heavy turn
    dom=collections.Counter()
    for d in H:
        best=max((k for k in (15,16,30,34,35) if k in d), key=lambda k:d[k], default=None); dom[names.get(best,'none')]+=1
    print('dominant farm scope on heavy turns:', dict(dom.most_common()))
    print('champion dist:', dict(collections.Counter(d['who'] for d in H).most_common()))
