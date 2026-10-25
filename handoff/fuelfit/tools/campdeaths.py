import json,glob,sys,collections
# campdeaths.py RES... : our deaths by r300 split by killer context (camp / champion / other), per game
for d in sys.argv[1:]:
    c=collections.Counter(); n=0
    for f in glob.glob(d+'/*/*.json'):
        j=json.load(open(f)); us='teamA' if '/A_' in f else 'teamB'; n+=1
        for e in j['events']:
            if e.get('kind')!='death' or e['owner'].get('team')!=us: continue
            for en in e['entries']:
                r=en['timestamp']['round']
                if r<=300:
                    ctx=en.get('context','?'); k='camp' if ctx=='camp' else ('champ' if ctx=='champion' else 'other')
                    c[k]+=1; c['all']+=1
                    if r<=100: c['r100']+=1
    print(d.ljust(16),'games',n,'deaths<=300/game',round(c['all']/max(1,n),2),'camp',round(c['camp']/max(1,n),2),'champ',round(c['champ']/max(1,n),2),'other',round(c['other']/max(1,n),2),'<=100',round(c['r100']/max(1,n),2))
