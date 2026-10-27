# bench_caps.py RESDIR... : our camp-group clears per game by window and kind (elk / gem cluster / gold-only / other) from the statistics JSON
import sys,json,glob,os,collections
T=json.load(open('/tmp/claude-0/ff/gem/cache/mapgroups.json'))
def kind(g):
    if 'elk' in g['kinds']: return 'elk'
    if g['gems']>0 and g['gold']<=0: return 'gem_clu'
    if g['gems']<=0: return 'gold_only'
    return 'mixed'
for d in sys.argv[1:]:
    files=glob.glob(f'/tmp/claude-0/ff/ws4/res/{d}/**/*.json',recursive=True); n=0; C=collections.Counter(); G=collections.Counter()
    for f in files:
        b=os.path.basename(f); side='teamA' if b.startswith('A_') else 'teamB'; m=b[2:-5]
        if m not in T: continue
        try: j=json.load(open(f))
        except Exception: continue
        n+=1
        for e in j['events']:
            if e['kind']!='campClear' or e['owner'].get('team')!=side: continue
            for en in e['entries']:
                r=en['timestamp']['round']
                if r>300: continue
                # the entry's x,y is where the clearing champion stood: nearest group centre within 5 (ids differ between stats and replay on some maps)
                best=min(T[m].values(), key=lambda g: max(abs(g['cx']-en['x']),abs(g['cy']-en['y'])))
                if max(abs(best['cx']-en['x']),abs(best['cy']-en['y']))>5: C[('far','?')]+=1; continue
                w='0-150' if r<=150 else '151-300'; k=kind(best); C[(w,k)]+=1; G[w]+=best['gems']
    if not n: print(d,'no games'); continue
    print(f"{d:18s} games {n:3d} | r0-150 elk {C[('0-150','elk')]/n:.2f} gem_clu {C[('0-150','gem_clu')]/n:.2f} gold_only {C[('0-150','gold_only')]/n:.2f} mixed {C[('0-150','mixed')]/n:.2f} gems {G['0-150']/n:.0f} | r151-300 elk {C[('151-300','elk')]/n:.2f} gem_clu {C[('151-300','gem_clu')]/n:.2f} gold_only {C[('151-300','gold_only')]/n:.2f} mixed {C[('151-300','mixed')]/n:.2f} gems {G['151-300']/n:.0f} | unmatched {C[('far','?')]/n:.2f}")
