# zagg.py RESDIR : percentiles per profiled id (per champion-turn), from the last [zp] block of each stdout
import zipfile,glob,sys,collections
N={1:'init',2:'shop',3:'vision',4:'groups',5:'foes',6:'camps(sec)',7:'support',8:'decide',9:'fight',10:'recall(sec)',11:'farm',12:'post',13:'log',
15:'choose_target',16:'step_towards',17:'engage',18:'best_altar',19:'br_altar_dist',20:'go_tribute',24:'other_captures',26:'evac',30:'near_camps',31:'monoguard',32:'awake_loop',33:'altar_lock',34:'br_plan',35:'br_legacy',40:'nc_tv',41:'nc_seen',42:'nc_state',43:'nc_push',44:'r_backhome',45:'r_recall',46:'r_bank',47:'r_group',48:'r_campfoe'}
H=collections.defaultdict(collections.Counter); M=collections.defaultdict(float)
for f in glob.glob(sys.argv[1]+'/**/*.repl26a',recursive=True):
    side='a' if '/A_' in f else 'b'
    L=[l[l.index('[zp]'):].split() for l in zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').replace('\x00','').splitlines() if '[zp]' in l]
    if not L: continue
    rmax=max(int(x[1]) for x in L)
    for x in L:
        if int(x[1])!=rmax: continue
        k=int(x[2]); M[k]=max(M[k],float(x[3]))
        for kv in x[4:]:
            b,v=kv.split(':'); H[k][int(b)]+=int(v)
def pct(h,q):
    n=sum(h.values()); c=0
    for b in sorted(h):
        c+=h[b]
        if c>=q*n: return b+1
print(f"{'id':16s} {'turns>0':>8s} {'p50':>5s} {'p90':>5s} {'p99':>5s} {'p99.9':>6s} {'max':>6s}  (k fuel; turns with cost>=1k counted from bucket 1)")
for k in sorted(H):
    h=H[k]; n=sum(h.values()); nz=n-h.get(0,0)
    print(f"{N.get(k,k):16s} {nz/n:8.1%} {pct(h,.5):5d} {pct(h,.9):5d} {pct(h,.99):5d} {pct(h,.999):6d} {M[k]/1000:6.1f}")
