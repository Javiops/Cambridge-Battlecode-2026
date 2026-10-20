"""Actor-only v1 feature/candidate contract and float32 reference for the WASM SIMD kernel."""
import math
import struct

G, C, H, K = 24, 12, 8, 16


def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


def encode(o: dict, terrain: dict) -> dict:
    m = o["self"]
    x, y, w, h = m["x"], m["y"], o["width"], o["height"]
    team, state = o["actor"]["team"], m["state"]
    distance = lambda p: max(abs(p[0]-x), abs(p[1]-y))
    altar = min(sorted(terrain["altars"], key=lambda p: (p[1], p[0])), key=distance)
    features = [m["health"]/max(1,m["max_health"]), m["strength"]/200, m["focus"]/200,
                m["gems"]/100, m["gold"]/1000, x/w, y/h, o["actor"]["round"]/2000,
                bool(state&8), bool(state&16), bool(state&2048), m["attack_range"]/8,
                m["move_speed"]/3, sum(c["team"]!=team for c in o["champions"])/10,
                sum(c["team"]==team for c in o["champions"])/10, len(o["camps"])/20,
                m["type"]/12, bool(state&(2|4|4096)), bool(state&1), len(o["vision"])/512,
                (altar[0]-x)/w, (altar[1]-y)/h, o["banks"][team]/1000, o["banks"][1-team]/1000]
    features = [f32(max(-4,min(4,v))) for v in features]
    rows = [[1,0,0,0,0,0,0,0,0,0,0,1]]
    actions = [{"kind":"wait"}]
    if state&2048:
        for a in o["abilities"]:
            if a["cooldown"] == 0 and ((a["kind"] == 1 and not state&16) or (a["kind"] == 7 and a["targets"]&8)):
                rows.append([0,0,0,1,0,0,0,m["health"]/2000,0,0,a["slot"]/2,1])
                action={"kind":"cast","slot":a["slot"]}
                if a["kind"]!=1: action["target"]={"kind":1,"id":m["id"]}
                actions.append(action)
    if state&16:
        targets = [(c,1) for c in sorted(o["champions"],key=lambda c:c["id"]) if c["team"]!=team]
        targets += [(c,2) for c in sorted(o["camps"],key=lambda c:c["id"])]
        count=0
        for t, kind in targets:
            if count>=4: break
            dx,dy=t["x"]-x,t["y"]-y
            if max(abs(dx),abs(dy)) <= m["attack_range"] and t["health"]>0:
                rows.append([0,0,1,0,dx/8,dy/8,max(abs(dx),abs(dy))/8,t["health"]/2000,
                             kind==1,kind==2,0,1]);count+=1
                actions.append({"kind":"attack","target":{"kind":kind,"id":t["id"]}})
    if state&8:
        for px,py in sorted(o["moves"],key=lambda p:(p[1],p[0])):
            dx,dy=px-x,py-y
            if max(abs(dx),abs(dy))==1:
                rows.append([0,1,0,0,dx/8,dy/8,1/8,0,0,0,0,1])
                actions.append({"kind":"move","x":px,"y":py})
                if len(rows)==K: break
    mask=[True]*len(rows)+[False]*(K-len(rows))
    rows += [[0]*C for _ in range(K-len(rows))]
    actions += [None]*(K-len(actions))
    return {"features":features,"candidates":[[f32(v) for v in row] for row in rows],"mask":mask,"actions":actions}


def weights():
    state=0xC0FFEE
    result=[]
    for _ in range(G*H+C*H+2*H+1):
        state=(1664525*state+1013904223)&0xffffffff
        result.append(f32(((state>>16)%512-256)/1024))
    return result


def infer(encoded, values=None):
    obs, candidates, mask = encoded["features"], encoded["candidates"], encoded["mask"]
    if len(obs)!=G or len(candidates)!=K or len(mask)!=K or any(len(c)!=C for c in candidates):
        raise ValueError("Wrong candidate model shape")
    flat=obs+[v for c in candidates for v in c]
    if not all(math.isfinite(v) for v in flat): raise ValueError("Model inputs must be finite")
    values=weights() if values is None else values
    if len(values)!=G*H+C*H+2*H+1 or not all(math.isfinite(v) for v in values):
        raise ValueError("Model weights must have the certified shape and be finite")
    wg=values[:G*H];wc=values[G*H:(G+C)*H]
    bias=values[(G+C)*H:(G+C+1)*H];out=values[(G+C+1)*H:-1]
    context=list(bias)
    for h in range(H):
        for g in range(G): context[h]=f32(context[h]+f32(wg[g*H+h]*obs[g]))
    scores=[]
    for candidate in candidates:
        lanes=[0.0]*4
        for h in range(H):
            value=context[h]
            for c in range(C): value=f32(value+f32(wc[c*H+h]*candidate[c]))
            lanes[h%4]=f32(lanes[h%4]+f32(out[h]*max(0,value)))
        score=f32(f32(f32(lanes[0]+lanes[1])+lanes[2])+lanes[3])
        scores.append(f32(score+values[-1]))
    return scores,max((i for i in range(K) if mask[i]),key=lambda i:scores[i])
