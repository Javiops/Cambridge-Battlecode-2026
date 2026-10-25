import json,glob,sys,collections,os
def evs(summ, tn):
    s=json.load(open(summ)); out=[]
    for e in s['events']:
        if e['kind']!='buyItem' or e['owner']['team']!=tn or e['owner']['name']!='Marcella': continue
        for x in e['entries']: out.append((x['timestamp']['round'], x['target']['name'], int(float(x['value']))))
    return sorted(out)
def jobs(w):
    if w=='t10':
        L=json.load(open('/mnt/project-files/online/data/t10_vs_band_1024/index.json'))['games']
        return [(g['summary'],'teamA' if g['side']=='a' else 'teamB') for g in L if not g.get('far') and g.get('summary') and '6' in g['draft']]
    return [(f,'teamA' if os.path.basename(f).startswith('A_') else 'teamB') for f in glob.glob(w+'/*/*.json')]
J=jobs(sys.argv[1]); C=collections.defaultdict(list); n=0; first=collections.Counter()
for summ,tn in J:
    E=evs(summ,tn)
    if not E: continue
    n+=1
    for R in (150,250,400):
        st=collections.Counter()
        for r,name,v in E:
            if r<R: st[name]+=v
        C[R].append(st)
    k=tuple(nm for r,nm,v in E[:3]); first[k]+=1
print(sys.argv[1],n)
for R in C:
    tot=collections.Counter()
    for st in C[R]: tot.update(st)
    strength=sum(v for k,v in tot.items() if 'Strength' in k)/n; bru=sum(v for k,v in tot.items() if 'Bruiser' in k)/n
    print(R, ' '.join(f"{k.replace(' Shard of ','-')}:{v/n:.1f}" for k,v in tot.most_common(8)), f"| str-shards {strength:.1f}")
for k,v in first.most_common(4): print(v,k)
for R in C:
    print(R,'total shards %.1f'%(sum(sum(st.values()) for st in C[R])/n))
