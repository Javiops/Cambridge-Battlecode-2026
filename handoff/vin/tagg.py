# tagg.py : per group (t10 / onl_cand / onl_base) and champion type, turns with nearest foe at d<=3 and d=4: attack / ability / move shares
import json,collections,os
S=os.path.dirname(os.path.abspath(__file__))
A=collections.defaultdict(collections.Counter)
for l in open(f'{S}/turn_list.txt'):
    z,t,g=l.split(); f=f'{S}/turn/{os.path.basename(z)[:-4]}.{t}.json'
    if not os.path.exists(f): continue
    for x in json.load(open(f)):
        b='d1' if x['fd']<=1 else ('d2-3' if x['fd']<=3 else ('d4' if x['fd']==4 else ('d5-6' if x['fd']<=6 else None)))
        if not b: continue
        k=(g,x['t'],b); A[k]['n']+=1; A[k]['atk']+=5 in x['kinds']; A[k]['ab']+=6 in x['kinds']; A[k]['mv']+=4 in x['kinds']; A[k]['hit']+=x['hit']
        A[k]['idle']+= not any(q in x['kinds'] for q in (4,5,6))
for ty in ('VesperVale','Marcella','Ryth','HeartOfRuin','Vendetta'):
    for b in ('d1','d2-3','d4','d5-6'):
        print(f'{ty:11s} {b:4s}',' | '.join(f"{g} n{A[(g,ty,b)]['n']} atk {A[(g,ty,b)]['atk']/max(1,A[(g,ty,b)]['n']):.0%} ab {A[(g,ty,b)]['ab']/max(1,A[(g,ty,b)]['n']):.0%} mv {A[(g,ty,b)]['mv']/max(1,A[(g,ty,b)]['n']):.0%} idle {A[(g,ty,b)]['idle']/max(1,A[(g,ty,b)]['n']):.0%}" for g in ('t10','onl_cand','onl_base')))
