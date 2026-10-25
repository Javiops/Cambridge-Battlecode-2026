import zipfile,glob,re,sys,collections
# idbg.py RESDIR : per map, per champion: ts, ng(groups), tiles, init step costs, wait, turn totals r1..r3 (unlimited fuel)
rows=[]
for f in sorted(glob.glob(sys.argv[1]+'/*.repl26a')):
    out=zipfile.ZipFile(f).read('team-a.stdout').decode('utf8','replace')
    ts=int(re.search(r'\[mapplan\] ts=(\d+)',out).group(1))
    pr=re.search(r'\[profile\] family=(\w+) ts=\d+ altars=(\d+) camps=(\d+) spawn_dist=(\d+) area=(\d+)',out)
    fam,alt,ng,sd,area=pr.groups()
    mp=f.split('/')[-1][4:-8]
    # steps come in champion program order; split by 'map' tag
    steps=re.findall(r'\[dbgI\] r(\d+) (\S+) (\d+)',out)
    champs=[]; cur=None
    for r,tag,v in steps:
        if tag=='map': cur={}; champs.append(cur)
        if cur is not None: cur[tag]=cur.get(tag,0)+int(v)
    used=collections.defaultdict(list)
    for r,v in re.findall(r'\[dbgT\] r(\d+) used (\d+)',out): used[int(r)].append(int(v))
    names=re.findall(r'\[init\] (\w+) ',out)
    rows.append((int(area),int(ng),ts,mp,fam,champs,used,names))
for area,ng,ts,mp,fam,champs,used,names in sorted(rows):
    init=[sum(v for k,v in c.items() if k!='wait') for c in champs]
    wait=[c.get('wait',0) for c in champs]
    print(f"{mp:<20} area={area:<5} ng={ng:<3} ts={ts} fam={fam:<6} init={init} wait={wait} r1={used.get(1)} r2={used.get(2)} r3={used.get(3)}")
    if '-v' in sys.argv:
        for n,c in zip(names,champs): print('   ',n[:5],{k:v for k,v in c.items()})
