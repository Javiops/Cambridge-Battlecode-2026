import sys,json,gzip,os,collections
T=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open('pcassets/replays_c37/index.json'))}
A=collections.Counter()
for fn in os.listdir('dec/'+T):
    us=side.get(T+'/'+fn.replace('.json.gz','.repl26a'))
    if us is None: continue
    try: D=json.load(gzip.open('dec/'+T+'/'+fn))
    except: continue
    st=D['meta'].get('stats')
    if not st: continue
    for c in st['champions']:
        w='us' if c['team']==us else 'them'; k=(w,c['typeName']); i=str(c['index'])
        A[k+('n',)]+=1; A[k+('cdd',)]+=c['championDamageDone']; A[k+('cdt',)]+=c['championDamageTaken']; A[k+('mdd',)]+=c['monsterDamageDone']; A[k+('K',)]+=c['kills']; A[k+('D',)]+=c['deaths']
        for r,kk in D['kinds'].items():
            ks=kk.get(i)
            if ks: A[k+('ab',)]+=ks.count(6); A[k+('at',)]+=ks.count(5); A[k+('t',)]+=1
types=sorted({k[1] for k in A})
print('type | side | n | abil/100t | atk/100t | champ dmg done | taken | monster dmg | K | D')
for t in types:
    for w in ('us','them'):
        n=A[(w,t,'n')]
        if n<5: continue
        tt=max(1,A[(w,t,'t')])
        print(t,w,n,round(100*A[(w,t,'ab')]/tt,1),round(100*A[(w,t,'at')]/tt,1),round(A[(w,t,'cdd')]/n),round(A[(w,t,'cdt')]/n),round(A[(w,t,'mdd')]/n),round(A[(w,t,'K')]/n,2),round(A[(w,t,'D')]/n,2))
