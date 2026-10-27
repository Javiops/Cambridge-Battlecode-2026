import os, sys, glob, pickle, json
from collections import defaultdict
W='/tmp/claude-0/w'; P=f'{W}/assets/pcassets'
TN={0:'Ryth',1:'Vesper',2:'Vendetta',7:'Marcella',12:'HoR',11:'Tavi',3:'Cassi',4:'Issac',5:'Stellar',6:'Prism',8:'Willow',9:'Ren',10:'Varg'}
def kind(g):
    ty=set(g.get('ty',[]))
    if ty & {4,5}: return 'boss'
    if 1 in ty: return 'elk'
    if 0 in ty: return 'wolf'
    if g['gems']<=0: return 'gold'
    return 'gem'
KINDS=('gold','gem','wolf','elk','boss')
def load():
    T=json.load(open(f'{P}/replays_t10/index.json')); C=json.load(open(f'{P}/replays_c34/index.json'))
    rows=[]
    for x in T:
        f=f'{W}/feat/t10/'+os.path.basename(x['file']).replace('.repl26a','.pkl')
        if not os.path.exists(f): continue
        F=pickle.load(open(f,'rb'))
        for t,s in ((0,'a'),(1,'b')):
            rows.append(dict(src='t10',map=x['map'],team=t,win=x[s+'_result']=='win',who=x[s],F=F))
    for x in C:
        if x['bot']!='e1foco': continue
        f=f'{W}/feat/e1foco/'+os.path.basename(x['file']).replace('.repl26a','.pkl')
        if not os.path.exists(f): continue
        F=pickle.load(open(f,'rb')); t=0 if x['side']=='a' else 1
        rows.append(dict(src='ours',map=x['map'],team=t,win=x['result']=='win',who='e1foco',F=F))
        rows.append(dict(src='riv',map=x['map'],team=1-t,win=x['result']!='win',who=x['rival'],F=F))
    return rows
def team_bin(row, b):
    F=row['F']; t=row['team']; out=defaultdict(float)
    T=F['T'].get((t,b))
    if not T: return None
    n=T['n']; out['alive']=T['alive']/n; out['ncl']=T['ncl']/n; out['big']=T['big']/n
    m=defaultdict(float)
    for (i,bb),f in F['F'].items():
        if bb!=b or F['team'][i]!=t: continue
        for k,v in f.items(): m[k]+=v
    if m['alive']:
        a=m['alive']
        for k in ('fr','own','home','al4','fo4','contact','hp'): out[k]=m[k]/a
        out['outn']=m['outn']/max(1,m['contact']); out['supn']=m['supn']/max(1,m['contact'])
    out['deaths']=m['death']
    # camp hits by kind and allies hitting same group same round
    H=[h for h in F['hits'] if h[0]//50==b and F['team'][h[1]]==t]
    by=defaultdict(set)
    for r,a,g in H: by[(r,g)].add(a)
    kc=defaultdict(float); fr=0; mates=0
    for (r,g),A in by.items():
        G=F['grp'][g]; kc[kind(G)]+=len(A); mates+=len(A)*len(A)
    tot=sum(kc.values())
    out['hitr']=tot
    for k in KINDS: out['h_'+k]=kc[k]/tot if tot else 0
    out['h_mates']=mates/tot if tot else 0   # mean squad size on a camp, weighted by champion-rounds
    caps=[c for c in F['caps'] if c[2]//50==b and c[1]==t]
    out['caps']=len(caps); out['capgems']=sum(F['grp'][c[0]]['gems'] for c in caps)
    return out
if __name__=='__main__':
    rows=load(); print(len(rows), file=sys.stderr)
    pickle.dump(rows,open(f'{W}/rows.pkl','wb'))
