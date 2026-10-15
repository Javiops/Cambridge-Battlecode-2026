"""Map-clustered candidate vs original spar-panel comparisons; no games run here."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse, json, math

ROOT = Path(__file__).resolve().parent
SPARS = ('spar11', 'spar12', 'spar16')

def sign_p(positive, negative):
    n = positive + negative
    if not n: return 1.0
    return min(1.0, 2 * sum(math.comb(n,k) for k in range(min(positive,negative)+1)) / 2**n)

def score(row):
    winner = {'teamA': 0, 'teamB': 1, 'draw': -1}[row['outcome']]
    return 0.5 if winner < 0 else float(winner == row['side'])

def load_rows(paths):
    rows = {}
    for p in paths:
        for r in json.loads(Path(p).read_text(encoding='utf-8'))['games']:
            key = (r['candidate'],r['opponent'],r['map_sha256'],r['side'])
            if key in rows:
                assert rows[key]['key'] == r['key'] and rows[key]['outcome'] == r['outcome'], key
            rows[key] = r
    return rows

def comparison(rows, name):
    result = {'candidate': name, 'spar': {}, 'original': {}}
    self_rows = [r for k,r in rows.items() if k[0]==name and k[1]=='original']
    if self_rows:
        maps = {}
        for r in self_rows: maps.setdefault(r['map_sha256'],{})[r['side']]=score(r)
        assert all(set(v)=={0,1} for v in maps.values())
        bw = sum(v[0]==v[1]==1 for v in maps.values())
        bl = sum(v[0]==v[1]==0 for v in maps.values())
        result['original'] = {'games':len(self_rows),'maps':len(maps),
            'wins':sum(score(r)==1 for r in self_rows),
            'losses':sum(score(r)==0 for r in self_rows),
            'draws':sum(score(r)==0.5 for r in self_rows),
            'both_won':bw,'both_lost':bl,'p_two_sided':sign_p(bw,bl)}
    deltas = {}
    panel_candidate = panel_original = 0
    map_sets = []
    for opponent in SPARS:
        subset=[r for k,r in rows.items() if k[0]==name and k[1]==opponent]
        if not subset: continue
        ids = Counter((r['map_sha256'],r['side']) for r in subset)
        assert all(n==1 for n in ids.values())
        ms={m for m,s in ids}; map_sets.append(ms)
        assert all((m,s) in ids for m in ms for s in (0,1))
        cs = bs = 0
        paired = {}
        for r in subset:
            base=rows[('original',opponent,r['map_sha256'],r['side'])]
            assert base['map_sha256']==r['map_sha256']
            assert base['identity']['runtime']==r['identity']['runtime']
            opponent_team = 'b' if r['side']==0 else 'a'
            assert base['identity']['wasm_'+opponent_team+'_sha256']==r['identity']['wasm_'+opponent_team+'_sha256'], 'Spar source differs'
            c,b=score(r),score(base); cs+=c; bs+=b
            paired[r['map_sha256']]=paired.get(r['map_sha256'],0)+(c-b)
            deltas[r['map_sha256']]=deltas.get(r['map_sha256'],0)+(c-b)
        positive=sum(x>0 for x in paired.values()); negative=sum(x<0 for x in paired.values())
        result['spar'][opponent]={'games':len(subset),'maps':len(ms),
            'candidate_win_score':cs,'original_win_score':bs,'score_delta':cs-bs,
            'percentage_point_delta':100*(cs-bs)/len(subset),
            'positive_maps':positive,'negative_maps':negative,
            'p_two_sided':sign_p(positive,negative)}
        panel_candidate+=cs; panel_original+=bs
    if map_sets:
        assert len(map_sets)==3 and all(m==map_sets[0] for m in map_sets), 'Incomplete spar panel'
        positive=sum(x>0 for x in deltas.values()); negative=sum(x<0 for x in deltas.values())
        result['panel']={'games':sum(v['games'] for v in result['spar'].values()),
            'maps':len(deltas),'candidate_win_score':panel_candidate,
            'original_win_score':panel_original,'score_delta':panel_candidate-panel_original,
            'percentage_point_delta':100*(panel_candidate-panel_original)/(6*len(deltas)),
            'positive_maps':positive,'negative_maps':negative,
            'neutral_maps':sum(x==0 for x in deltas.values()),
            'p_two_sided':sign_p(positive,negative)}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('paths',nargs='+');p.add_argument('--names',nargs='+',required=True);p.add_argument('--out')
    a=p.parse_args();rows=load_rows(a.paths)
    output={n:comparison(rows,n) for n in a.names}
    if a.out:
        dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))
