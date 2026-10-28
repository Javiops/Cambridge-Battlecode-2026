r"""shop13dec.py REPLAY OUT.json.gz   (MAXR env, default 600)
Three bounded passes of pcassets/viewer/replaydump.js (same wasm pick as ext.py):
 --raw    : per round, per champion [idx, team, type, x, y, hp, mhp, gems, gold, alive, strength_total, focus_total, {item_idx: count}]
            (snapshot champion struct, engine 2.0.0: strength total f32 @148, focus total f32 @132, items u32[84] @240)
 --camps  : camp static table [idx,type,group,spawnX,spawnY,gems,gold,maxHp,respawnDelay], captures [group, team, round], per round
            alive camps / damaged camp hp / group states (as ext.py)
 --deltas : every step by a champion that damaged a camp: [round, actor, camp_idx, dmg, step_kind]
"""
import sys, os, json, gzip, subprocess, struct
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.join(HERE, '..', 'pcassets', 'viewer', 'replaydump.js')
MAXR = int(os.environ.get('MAXR', '600'))
GS = {'unknown': 0, 'alive': 1, 'reward_available': 2, 'respawning': 3}

def run(rep, args):
    return subprocess.Popen(['node', RD, rep] + args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)

def f32(x): return struct.unpack('<f', struct.pack('<I', x))[0]

def extract(rep):
    # pass 1: raw champion structs
    p = run(rep, ['--raw']); rounds = []
    for l in p.stdout:
        d = json.loads(l)
        if not d['raw']: continue
        r = d['round']
        if r > MAXR: break
        C = []
        for w in d['raw']:
            items = {i: w[60 + i] for i in range(84) if w[60 + i]}
            C.append([w[1], w[2], w[3], w[5] if w[5] < 2**31 else w[5] - 2**32, w[6] if w[6] < 2**31 else w[6] - 2**32,
                      round(f32(w[7]), 1), round(f32(w[8]), 1), w[59], w[58], w[56], round(f32(w[37]), 1), round(f32(w[33]), 1), items])
        rounds.append({'r': r, 'c': C})
    p.kill(); p.wait()
    # pass 2: camps
    p = run(rep, ['--camps']); camps = None; caps = []; prevgs = {}; prevct = {}; kr = {}
    for l in p.stdout:
        d = json.loads(l)
        if d.get('summary') or d.get('draft'): continue
        r = d['round']
        if r > MAXR: break
        K = d.get('camps') or []
        if camps is None:
            camps = [[k['index'], k['type'], k['group'], k['spawnX'], k['spawnY'], k.get('rewardGems'), k.get('rewardGold'), k['maxHealth'], k.get('respawnDelay')] for k in K]
        gs = {}; ct = {}
        for k in K:
            g = k['group']; gs[g] = GS.get(k['groupStateName'], 0)
            if k['captureTeam'] != 2: ct[g] = k['captureTeam']
        for g, s in gs.items():
            if prevgs.get(g) == 2 and s == 3: caps.append([g, prevct.get(g, ct.get(g, -1)), r])
        kr[r] = {'ka': [k['index'] for k in K if k['alive']], 'kaw': [k['index'] for k in K if k['alive'] and k['awake']],
                 'khp': [[k['index'], int(k['health'])] for k in K if k['alive'] and k['health'] < k['maxHealth']], 'gs': gs}
        prevgs = gs; prevct = ct
    p.kill(); p.wait()
    pos2camp = [k[0] for k in camps] if camps else []
    # pass 3: deltas (camp damage per step)
    p = run(rep, ['--deltas']); ck = []; cc = []
    team = {c[0]: c[1] for c in rounds[0]['c']} if rounds else {}
    for l in p.stdout:
        d = json.loads(l); r = d['r']
        if r > MAXR: break
        if d['ak'] != 1: continue
        a = d['ai']
        for i, x in d.get('dk', []):
            if x < 0 and i < len(pos2camp): ck.append([r, a, pos2camp[i], round(-x, 1), d['k']])
        for i, x in d.get('dc', []):
            if x < 0 and team.get(i) is not None and team.get(i) != team.get(a): cc.append([r, a, i, round(-x, 1)])
    p.kill(); p.wait()
    for rr in rounds: rr.update(kr.get(rr['r'], {}))
    return {'file': os.path.basename(rep), 'camps': camps, 'caps': caps, 'rounds': rounds, 'ck': ck, 'cc': cc}

if __name__ == '__main__':
    rep, out = sys.argv[1], sys.argv[2]
    D = extract(rep)
    json.dump(D, gzip.open(out + '.tmp', 'wt'), separators=(',', ':'))
    os.replace(out + '.tmp', out)
    print(out, len(D['rounds']), 'rounds', len(D['caps']), 'caps', len(D['ck']), 'ck')
