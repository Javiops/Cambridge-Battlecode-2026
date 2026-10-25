# fpt_st.py RESDIR [THR]: heavy turns (tot >= THR) split by section 10 (tribute) / 11 (farm): scope means
import zipfile,glob,sys,collections,statistics as st
names={14:'st:setup',36:'st:ct1',40:'st:ct2jam',41:'st:isle',42:'st:fallback',29:'st:tpc',38:'st:dashhole',37:'st:move',16:'step_towards',20:'go_tribute',18:'best_altar',19:'br_altar_dist',15:'choose_target',30:'engage_camp',10:'RECALL/TRIB',11:'FARM',9:'fight',8:'decide',3:'vision',4:'groups',5:'foes',6:'camps',2:'shop',1:'init',12:'post',13:'log',24:'other_captures',31:'refresh_groups',32:'near_camps',33:'farm()',21:'ct:lead',22:'ct:pfclaims',23:'ct:compute',25:'ct:pd_gd',27:'ct:score',28:'ct:top'}
THR=float(sys.argv[2]) if len(sys.argv)>2 else 76000
rows=[]; games=0; turns=0
for f in glob.glob(sys.argv[1]+'/*/*.repl26a')+glob.glob(sys.argv[1]+'/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    try: t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    except KeyError: continue
    games+=1
    for l in t:
        if '[fpn]' in l: turns=max(turns,0)
        if '[fpt]' not in l: continue
        p=l[l.index('[fpt]')+5:].split(); d={'r':int(p[0][1:]),'who':p[1],'tot':float(p[2].split('=')[1]),'g':f.split('/')[-1]}
        for kv in p[3:]:
            k,v=kv.split('='); d[int(k)]=float(v)
        rows.append(d)
H=[d for d in rows if d['tot']>=THR]
print(f'games {games}; [fpt] turns {len(rows)}; tot>={THR:.0f}: {len(H)}')
for sec,lab in ((10,'TRIBUTE'),(11,'FARM')):
    S=[d for d in H if d.get(sec,0)>=max(d.get(10,0),d.get(11,0),1)]
    if not S: continue
    print(f'--- {lab} heavy turns: {len(S)}; tot median {st.median(d["tot"] for d in S):.0f} max {max(d["tot"] for d in S):.0f}; rounds r<=50 {sum(1 for d in S if d["r"]<=50)} r51-300 {sum(1 for d in S if 50<d["r"]<=300)} r>300 {sum(1 for d in S if d["r"]>300)}')
    print(f"{'scope':16}{'mean':>8}{'present%':>9}{'mean|pres':>11}{'max':>8}")
    for k in sorted(names):
        v=[d.get(k,0) for d in S]; pres=[x for x in v if x>0]
        if not pres or st.mean(v)<1000: continue
        print(f"{names[k]:16}{st.mean(v):8.0f}{100*len(pres)/len(S):8.0f}%{st.mean(pres):11.0f}{max(v):8.0f}")
    print('maps:', dict(collections.Counter(d['g'] for d in S).most_common(8)))
