# rtop.py BASE VAR OPP: stats-json comparison of our team, all games and flip games (base won, var lost)
import json,glob,os,sys,collections
B,V,O=sys.argv[1:4]
def tl(runs,r):
    t=0;v=0
    for x in runs:
        if t>r: break
        v=int(x['value']); t+=x['duration']
    return v
def one(f):
    j=json.load(open(f)); side=os.path.basename(f)[0]; us='teamA' if side=='A' else 'teamB'
    win=(j['match']['outcome']=='teamA')==(side=='A')
    D=collections.Counter(); deaths=[]; clears=[]
    for e in j['events']:
        o=e['owner']
        if o.get('team')!=us: continue
        for x in e['entries']:
            r=x['timestamp']['round']
            if e['kind']=='death':
                deaths.append((r,x['x'],x['y'],x['context']))
            if e['kind']=='campClear': clears.append((r,x['target'].get('id'),x['context']))
    for r,xx,yy,c in deaths:
        b='early' if r<=150 else 'mid' if r<=400 else 'late'
        D[f'death_{b}']+=1; D[f'death_{c}']+=1
        if r<=400:
            twin=any(abs(r-r2)<=5 and max(abs(xx-x2),abs(yy-y2))<=6 and (r2,x2,y2)!=(r,xx,yy) for r2,x2,y2,_ in deaths)
            D['d400_twin' if twin else 'd400_solo']+=1
            if c=='camp': D['d400_camp']+=1
    # clears: dedupe same group+round (multiple champions credited?)
    cs=set((r,g) for r,g,_ in clears)
    D['clears400']=sum(1 for r,g in cs if r<=400); D['clears150']=sum(1 for r,g in cs if r<=150)
    D['clears_all']=len(cs)
    for t in j['teamTimelines']:
        if t['owner']==us and t['metric']=='submittedGems':
            D['gems150']=tl(t['runs'],150); D['gems300']=tl(t['runs'],300); D['gems400']=tl(t['runs'],400)
    D['gold']=sum(int(c['metrics'].get('earnedGold',0)) for c in j['champions'] if c.get('team',None)==us) if 'team' in j['champions'][0] else 0
    return win,D
fs=sorted(glob.glob(f'{B}/{O}/*.json'))
A=collections.defaultdict(collections.Counter); N=collections.Counter()
for f in fs:
    k=os.path.basename(f); g=f'{V}/{O}/{k}'
    if not os.path.exists(g): continue
    wb,db=one(f); wv,dv=one(g)
    for grp in ['all']+(['flip-'] if wb and not wv else [])+(['flip+'] if wv and not wb else []):
        N[grp]+=1; A[grp,'base'].update(db); A[grp,'var'].update(dv)
keys=['death_early','death_mid','death_late','death_camp','death_champion','d400_camp','d400_twin','d400_solo','clears150','clears400','clears_all','gems150','gems300','gems400']
for grp in ('all','flip-','flip+'):
    n=max(1,N[grp]); print(f'== {grp} n={N[grp]}')
    for k in keys: print(f'  {k:15s} base {A[grp,"base"][k]/n:7.2f}  var {A[grp,"var"][k]/n:7.2f}')
