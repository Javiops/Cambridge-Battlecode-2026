r"""ext.py REPLAY.zip OUT.json.gz
Decode one replay in two fast passes, whole game. Engine 1.0.3 or 2.0.0: replaydump.js (this folder, patched for the 2.0.0
snapshot layout) picks the engine wasm matching the replay from the cambc asset cache (%LOCALAPPDATA%\cambc\assets, filled
by cambc 4.0.0); CAMBC_VIS_WASM still overrides. Same dec2 format as lab\top10\scripts\ext.py.
 1. per-round state (--camps --vis): champions [idx,team,type,x,y,hp,mhp,gems,gold,alive,cd0,cd1,respawn] per round,
    vision per champion (enemy champion indices that champion's own perspective shows; None if dead),
    camp static table [idx,type,group,spawnX,spawnY,groupGems,groupGold,maxHp,respawnDelay], alive camps and damaged camp hp
    per round, group state per round, captures [group, team, round].
 2. per-step health deltas (--deltas), attributed to the step's actor:
    cc champion->enemy champion damage, ck champion->camp damage, kc camp->champion damage, heal champion->ally (+hp),
    kinds: step kinds per champion turn (4 move, 5 attack, 6 ability; kind 3 dropped).
All dicts keyed by round (string) then 'actor>target'."""
import sys, os, json, gzip, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ)
RD = os.path.join(HERE, 'replaydump.js')
GS = {'unknown': 0, 'alive': 1, 'reward_available': 2, 'respawning': 3}

def run(rep, args):
    return subprocess.Popen(['node', RD, rep] + args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=ENV, bufsize=1 << 20)

def extract(rep):
    p = run(rep, ['--camps', '--vis'])
    rounds = []; camps = None; caps = []; prevgs = {}; prevct = {}; summ = None
    for l in p.stdout:
        d = json.loads(l)
        if d.get('summary'): summ = d; continue
        if d.get('draft'): continue
        r = d['round']
        C = [[c['index'], c['team'], c['type'], c['x'], c['y'], c['health'], c['maxHealth'], c['gems'], c['gold'], int(c['alive']),
              c['cd'][0], c['cd'][1], c['respawn']] for c in d['champions']]
        K = d.get('camps') or []
        if camps is None:
            camps = [[k['index'], k['type'], k['group'], k['spawnX'], k['spawnY'], k.get('rewardGems'), k.get('rewardGold'), k['maxHealth'], k.get('respawnDelay')] for k in K]
        gs = {}; ct = {}; alive = []
        for k in K:
            g = k['group']; gs[g] = GS.get(k['groupStateName'], 0)
            if k['captureTeam'] != 2: ct[g] = k['captureTeam']
            if k['alive']: alive.append(k['index'])
        for g, s in gs.items():
            if prevgs.get(g) == 2 and s == 3:
                caps.append([g, prevct.get(g, ct.get(g, -1)), r])
        hp = [[k['index'], int(k['health'])] for k in K if k['alive'] and k['health'] < k['maxHealth']]
        aw = [k['index'] for k in K if k['alive'] and k['awake']]
        rounds.append({'r': r, 'c': C, 'v': d.get('vis'), 'ka': alive, 'kaw': aw, 'khp': hp, 'gs': gs, 'sg': d.get('submittedGems')})
        prevgs = gs; prevct = ct
    p.wait()
    team = {c[0]: c[1] for c in rounds[0]['c']} if rounds else {}
    pos2camp = [k[0] for k in camps] if camps else []
    cc, ck, kc, heal, kinds = {}, {}, {}, {}, {}
    def add(D, r, key, x):
        dd = D.setdefault(r, {}); dd[key] = round(dd.get(key, 0) + x, 2)
    p = run(rep, ['--deltas'])
    for l in p.stdout:
        d = json.loads(l); r = d['r']; ak = d['ak']; a = d['ai']
        if ak == 1:
            if d['k'] != 3:
                kk = kinds.setdefault(r, {}).setdefault(a, [])
                if d['k'] not in kk: kk.append(d['k'])
            at = team.get(a)
            for i, x in d.get('dc', []):
                if x < 0 and team.get(i) is not None and team.get(i) != at: add(cc, r, f'{a}>{i}', -x)
                elif x > 0 and team.get(i) == at: add(heal, r, f'{a}>{i}', x)
            for i, x in d.get('dk', []):
                if x < 0 and i < len(pos2camp): add(ck, r, f'{a}>{pos2camp[i]}', -x)
        elif ak == 2:
            for i, x in d.get('dc', []):
                if x < 0: add(kc, r, f'{a}>{i}', -x)
    p.wait()
    meta = {'file': os.path.basename(rep), 'final': summ and summ.get('finalRound'), 'outcome': summ and summ.get('outcome'),
            'gems': summ and summ.get('submittedGems'), 'stats': summ and summ.get('statistics')}
    return {'meta': meta, 'camps': camps, 'caps': caps, 'rounds': rounds, 'cc': cc, 'ck': ck, 'kc': kc, 'heal': heal, 'kinds': kinds}

if __name__ == '__main__':
    rep, out = sys.argv[1], sys.argv[2]
    D = extract(rep)
    json.dump(D, gzip.open(out + '.tmp', 'wt'), separators=(',', ':'))
    os.replace(out + '.tmp', out)
    print(out, len(D['rounds']), 'rounds', len(D['caps']), 'caps', sum(len(v) for v in D['cc'].values()), 'cc', sum(len(v) for v in D['ck'].values()), 'ck')
