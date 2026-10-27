import json,gzip,os,sys,glob
from collections import defaultdict,Counter
W='/tmp/claude-0/w';P=f'{W}/assets/pcassets'
TN={0:'Ryth',1:'Vesper',2:'Vendetta',7:'Marcella',12:'HoR',11:'Tavi',3:'Cassi',4:'Issac',5:'Stellar',6:'Prism',8:'Willow',9:'Ren',10:'Varg'}
T=json.load(open(f'{P}/replays_t10/index.json'));C=json.load(open(f'{P}/replays_c34/index.json'))
om=set(x['map'] for x in C if x['bot']=='e1foco')
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
def game(path,t,r0=50,r1=300):
    D=json.load(gzip.open(path)); pair=Counter(); alive=Counter(); stab=[]; part=defaultdict(Counter)
    for row in D['rounds']:
        if not(r0<=row['r']<r1): continue
        A=[c for c in row['c'] if c[1]==t and c[9]]
        for c in A:
            alive[c[2]]+=1
            near=[(ch(c,d),d) for d in A if d is not c and ch(c,d)<=4]
            if near: part[c[2]][min(near,key=lambda x:x[0])[1][2]]+=1
            for d in A:
                if d[0]>c[0] and ch(c,d)<=4: pair[tuple(sorted((c[2],d[2])))]+=1
    return pair,alive,part
def run(sel):
    PA=Counter(); AL=Counter(); PT=defaultdict(Counter); n=0
    for path,t in sel:
        if not os.path.exists(path): continue
        p,a,pt=game(path,t); PA.update(p); AL.update(a); n+=1
        for k,v in pt.items(): PT[k].update(v)
    return PA,AL,PT,n
selW=[];selO=[]
for x in T:
    if x['map'] not in om: continue
    f=f'{W}/dec/t10/'+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    for t,s in ((0,'a'),(1,'b')):
        if x[s+'_result']=='win': selW.append((f,t))
for x in C:
    if x['bot']=='e1foco':
        selO.append((f'{W}/dec/e1foco/'+os.path.basename(x['file']).replace('.repl26a','.json.gz'),0 if x['side']=='a' else 1))
for lab,sel in (('T10W',selW),('OURS',selO)):
    PA,AL,PT,n=run(sel); print('==',lab,n,'games, r50-300')
    for (a,b),v in PA.most_common(12):
        print(f'  {TN[a]:9}+{TN[b]:9} within4 share of a-alive {v/AL[a]:.2f} of b-alive {v/AL[b]:.2f}')
    for a in (12,1,7,2,0):
        tot=sum(PT[a].values())
        if tot: print('  nearest mate of',TN[a],' '.join(f'{TN[k]}:{v/AL[a]:.2f}' for k,v in PT[a].most_common(4)))
