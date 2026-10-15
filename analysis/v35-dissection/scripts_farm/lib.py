import json, glob, collections, statistics as st, os
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
G=[json.load(open(f)) for f in sorted(glob.glob(S+'/ws2/scripts_farm/out/*.json'))]
MAPS='collision corners elkring expanse interlock lanes monolith packs rows'.split()
TIERS=['top10','11-20','21-30','other']
def med(v): return st.median(v) if v else float('nan')
def mean(v): return st.mean(v) if v else float('nan')
def p(v,q):
    v=sorted(v); return v[min(len(v)-1,int(q*len(v)))] if v else float('nan')
def champs(g,team): return [c for c in g['champs'] if c['team']==team]
def alive_rounds(c): return sum(v for k,v in c['states'].items() if k!='dead')
def splits():
    out=[('all',G)]
    out+= [('map '+m,[g for g in G if g['map']==m]) for m in MAPS]
    out+= [('win',[g for g in G if g['res']=='win']),('loss',[g for g in G if g['res']=='loss'])]
    out+= [('opp '+t,[g for g in G if g['tier']==t]) for t in TIERS]
    return out
def tbl(header,rows):
    print('| '+' | '.join(header)+' |'); print('|'+'---|'*len(header))
    for r in rows: print('| '+' | '.join(str(x) for x in r)+' |')
    print()
def f(x,d=1): 
    try: return f'{x:.{d}f}'
    except: return str(x)
