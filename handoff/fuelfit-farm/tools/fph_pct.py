# fph_pct.py RESDIR: percentiles per section/scope from the last [fph] block of every team stdout (a1p profiling build)
import zipfile,glob,sys,collections
names={0:'pre-sweep',1:'init',2:'shop',3:'vision',4:'groups',5:'foes',6:'camps',7:'support',8:'decide/flee',9:'fight',10:'recall/tribute',11:'farm',12:'post-sweep',13:'log',15:'choose_target',16:'step_towards',17:'engage',18:'best_altar',19:'br_altar_dist',20:'go_tribute',24:'other_captures',26:'evac',30:'engage_camp',31:'refresh_groups',32:'near_camps',33:'farm()',34:'my_dps',35:'allies_near',39:'TOTAL'}
H=collections.defaultdict(lambda:[0]*40); N=0; files=0
for f in glob.glob(sys.argv[1]+'/*.repl26a')+glob.glob(sys.argv[1]+'/*/*.repl26a'):
    z=zipfile.ZipFile(f)
    for side in 'ab':
        try: t=z.read(f'team-{side}.stdout').decode('latin1').splitlines()
        except KeyError: continue
        idx=[i for i,l in enumerate(t) if '[fpn]' in l]
        if not idx: continue
        i=idx[-1]; N+=int(t[i].split()[-1]); files+=1
        for l in t[i+1:]:
            if '[fph]' not in l: break
            p=l[l.index('[fph]')+5:].split(); k=int(p[0])
            for b,v in enumerate(p[1:41]): H[k][b]+=int(v)
def pct(h,q):
    n=sum(h); c=0
    for b,v in enumerate(h):
        c+=v
        if c>=q*n: return (b+1)*2.5
    return 100
print(f'teams {files} turns {N}')
print(f"{'section':16}{'p50':>6}{'p90':>6}{'p99':>6}{'p99.9':>7}{'max-bucket':>11}{'share>25k':>10}")
for k in sorted(H):
    h=H[k]; n=sum(h); mb=max(b for b,v in enumerate(h) if v) if n else 0
    print(f"{names.get(k,str(k)):16}{pct(h,.5):6.1f}{pct(h,.9):6.1f}{pct(h,.99):6.1f}{pct(h,.999):7.1f}{(mb+1)*2.5:10.1f}{'+' if mb==39 else ' '}{100*sum(h[10:])/max(1,n):9.2f}%")
