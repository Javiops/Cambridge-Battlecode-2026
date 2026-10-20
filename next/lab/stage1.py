"""Executable Stage 1 exit checks. Diagnostic traces are not a training dataset."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import time
import zipfile

from . import core, mapgen, policy, stats, report
from .environment import Environment

PICKS = [[0, 5, 11, 10, 3]] * 2


def sources():
    files=["lab.toml"]+[p.relative_to(core.ROOT).as_posix() for p in sorted((core.ROOT/"lab").iterdir())
                        if p.suffix in (".py",".mjs")]
    files += [p.relative_to(core.ROOT).as_posix() for p in sorted((core.ROOT/"bots/contract-probe/src").glob("*")) if p.is_file()]
    # Git checkouts may translate CRLF/LF; source identity ignores that transport detail.
    return {p:hashlib.sha256((core.ROOT/p).read_text(encoding="utf-8").encode()).hexdigest() for p in files}


def json_sha(path):
    return hashlib.sha256(json.dumps(json.loads(path.read_text()),sort_keys=True,separators=(",",":")).encode()).hexdigest()


def traces(replay: Path) -> dict:
    rows = {}
    with zipfile.ZipFile(replay) as archive:
        for team, name in enumerate(("team-a.stdout", "team-b.stdout")):
            data = archive.read(name)
            pos = 0
            while (pos := data.find(b"S1B!", pos)) >= 0:
                r, champion, budget, kernel, total, pick, moves, length = struct.unpack_from("<8I", data, pos+4)
                pos += 36
                features = list(struct.unpack_from("<24f", data, pos)); pos += 96
                candidates = [list(struct.unpack_from("<12f", data, pos+48*i)) for i in range(16)]; pos += 768
                mask = list(struct.unpack_from("<16?", data, pos)); pos += 16
                scores = list(struct.unpack_from("<16f", data, pos)); pos += 64
                tiles = [list(struct.unpack_from("<2i", data, pos+8*i)) for i in range(moves)]; pos += 8*moves
                actions = json.loads(data[pos:pos+length]); pos += length
                key = (r, champion)
                if key in rows:
                    raise ValueError("Duplicate or resumed fuel-exhausted probe trace")
                rows[key] = dict(team=team, budget=budget, kernel=kernel, total=total, pick=pick,
                                 features=features, candidates=candidates, mask=mask, scores=scores,
                                 moves=tiles, actions=actions)
    return rows


def close_float(a, b):
    if isinstance(a, list):
        return len(a) == len(b) and all(close_float(x, y) for x, y in zip(a, b))
    return abs(a-b) <= 2e-6


def verify_map(map_name: str, version: core.Version, profile: dict) -> dict:
    out = core.ROOT / ".cambc/stage1" / map_name.replace("/", "_")
    out.mkdir(parents=True, exist_ok=True)
    raw, error = core.run_game(version, version, core.map_path(map_name), str(out), logs=True, profile=profile)
    if raw is None:
        raise ValueError(error)
    summary = stats.summarize(raw)
    if any(t["faults"] or t["fuel_exhausted"] for t in summary["teams"].values()):
        raise ValueError(f"{map_name}: probe faults or fuel exhaustion")
    replay = max(out.glob("*.repl26a"), key=lambda p: p.stat().st_mtime)
    rows = traces(replay)
    expected = len(raw["roster"]["champions"])*80
    if len(rows) != expected:
        raise ValueError(f"{map_name}: incomplete trace: {len(rows)} != {expected}")
    actions = collections.Counter()
    checked = 0
    with Environment() as env:
        reset = env.reset(map_name, PICKS)
        eid, o, terrain = reset["env_id"], reset["observation"], reset["terrain"]
        while not o["done"]:
            actor = o["actor"]
            if actor["round"] > 80:
                o = env.request(op="finish_wait", env_id=eid, limit=50000)["observation"]
                if not o["done"]: raise ValueError("Incomplete native terminal replay")
                continue
            key = (actor["round"], actor["champion"])
            if actor["round"] <= 80:
                if key not in rows:
                    raise ValueError(f"Missing actor trace {key}")
                trace = rows[key]
                encoded = policy.encode(o, terrain)
                for k in ("features", "candidates", "mask"):
                    if not close_float(encoded[k], trace[k]):
                        raise ValueError(f"{map_name} {key}: {k} parity failed: {encoded[k]} != {trace[k]}")
                if sorted(o["moves"]) != sorted(trace["moves"]):
                    raise ValueError(f"{map_name} {key}: movement mask parity failed")
                scores, chosen = policy.infer(encoded)
                if not close_float(scores, trace["scores"]) or chosen != trace["pick"]:
                    raise ValueError(f"{map_name} {key}: float32 inference parity failed")
                checked += 1
                ended = False
                for attempt in trace["actions"]:
                    step = env.step(eid, actor, attempt["action"])
                    if step["error_code"] != attempt["code"] or step["result"] != attempt["result"]:
                        raise ValueError(f"{map_name} {key}: action parity failed: {attempt} != {step}")
                    actions[attempt["action"]["kind"]] += 1
                    ended, o = step["turn_ended"], step["observation"]
                if ended:
                    continue
            o = env.step(eid, actor, {"kind": "wait"})["observation"]
        terminal = o["terminal"]
        banks = [summary["teams"][t]["gems"] for t in ("teamA", "teamB")]
        if terminal != dict(outcome=summary["outcome"], round=summary["rounds"], banks=banks):
            raise ValueError(f"{map_name}: terminal parity failed: {terminal}")
    ordinary = [r for r in rows.values() if r["budget"] == 100000]
    kernel = max(r["kernel"] for r in ordinary)
    if kernel > core.config()["stage1"]["max_kernel_fuel"]:
        raise ValueError(f"{map_name}: kernel fuel {kernel} exceeds the certified envelope")
    if max(r["total"] for r in ordinary)>core.config()["stage1"]["max_prelog_fuel"]:
        raise ValueError(f"{map_name}: insufficient full-turn fuel headroom")
    return dict(map=map_name, map_sha256=core.sha(core.map_path(map_name)), actors=len(raw["roster"]["champions"]),
                observations=checked, actions=dict(actions), kernel_fuel_max=kernel,
                prelog_fuel_max=max(r["total"] for r in ordinary), terminal=terminal,
                faults=0, fuel_exhausted=0, wasm_sha256=core.sha(version.wasm))


def verify() -> dict:
    profile = core.runtime_identity()
    bot = core.ROOT / "bots/contract-probe"
    built = subprocess.run([core.CLI, "build", "--release", str(bot)], cwd=core.ROOT, env=core.ENV,
                           capture_output=True, text=True, timeout=core.TIMEOUT)
    if built.returncode:
        raise ValueError(built.stdout[-3000:]+built.stderr[-3000:])
    v = core.Version("contract-probe", bot/".cambc/build-release/bot-injected.wasm", {})
    result = dict(schema=1, runtime=profile, engine_wasm_sha256=core.sha(mapgen.engine_path()),
                  protocol=verify_protocol(), model=dict(global_features=policy.G, candidate_features=policy.C, hidden=policy.H,
                             candidates=policy.K, weights=len(policy.weights()), decisions_per_turn=2), maps=[])
    for name in core.config()["stage1"]["parity_maps"]:
        print("Verifying " + name, flush=True)
        result["maps"].append(verify_map(name, v, profile))
    result["passed"] = True
    save("stage1-parity.json", result)
    return result


def verify_protocol() -> dict:
    with Environment() as env:
        a, b = [env.reset("00collision", PICKS) for _ in range(2)]
        actor = a["observation"]["actor"]
        def rejected(**command):
            try: env.request(**command)
            except ValueError: return
            raise ValueError("Invalid request was accepted: "+str(command))
        rejected(op="step", env_id=a["env_id"], actor={**actor,"team":1}, action={"kind":"wait"})
        rejected(op="step", env_id=a["env_id"], actor=actor, action={"kind":"cast","slot":99})
        rejected(op="step", env_id=a["env_id"], actor=actor, action={"kind":"move","x":2**40,"y":0})
        first=env.step(a["env_id"],actor,{"kind":"priority","priority":0})
        assert not first["turn_ended"]
        second=env.step(a["env_id"],actor,{"kind":"priority","priority":0})
        assert second["turn_ended"]
        rejected(op="step", env_id=a["env_id"], actor=actor, action={"kind":"wait"})
        batch=env.batch_steps([("unknown",actor,{"kind":"wait"}),
                               (b["env_id"],b["observation"]["actor"],{"kind":"wait"})])
        assert [r["ok"] for r in batch]==[False,True]
        assert "terminal" not in batch[1]["result"]["observation"]
        env.close_episode(a["env_id"])
        rejected(op="observe",env_id=a["env_id"])
        rejected(op="reset",map=str(core.map_path("00collision")),picks=[[0,0,0],[0,1,2]])
    native=subprocess.run([mapgen.node(),"--no-warnings",str(core.ROOT/"lab/engine-check.mjs"),
                           str(mapgen.engine_path()),str(core.map_path("00collision"))],
                          capture_output=True,text=True,cwd=core.ROOT,timeout=30)
    if native.returncode: raise ValueError(native.stderr[-2000:])
    return json.loads(native.stdout)|dict(stale_actor_rejected=True,decision_cap=2,batch_error_isolation=True,
                                        invalid_numeric_input_rejected=True,closed_episode_rejected=True)


def save(name, result):
    result["sources"] = sources()
    (core.ROOT/"results"/name).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")


def benchmark() -> dict:
    jobs = core.config()["stage1"]["benchmark_envs"]
    steps = core.config()["stage1"]["benchmark_steps"]
    with Environment() as env:
        episodes = [env.reset(core.config()["maps"]["screen"][i], PICKS) for i in range(jobs)]
        start = time.perf_counter()
        for _ in range(steps):
            replies = env.request(op="batch", commands=[dict(op="step", env_id=e["env_id"],
                actor=e["observation"]["actor"], action={"kind":"wait"}) for e in episodes])
            for e, r in zip(episodes, replies):
                if not r["ok"]: raise ValueError(r["error"])
                e["observation"] = r["result"]["observation"]
                if e["observation"]["done"]: raise ValueError("Benchmark exhausted an episode")
        elapsed = time.perf_counter()-start
        start = time.perf_counter()
        completed=[]
        for e in episodes:
            reply=env.request(op="finish_wait",env_id=e["env_id"],limit=50000)
            if not reply["observation"]["done"]: raise ValueError("Incomplete full-game benchmark")
            completed.append(reply)
        tail_time=time.perf_counter()-start
    result = dict(schema=1, passed=True, engine_wasm_sha256=core.sha(mapgen.engine_path()), environments=jobs,
                  observed_actor_turns=jobs*steps, seconds=elapsed, actor_turns_per_second=jobs*steps/elapsed,
                  idle_tail_turns=sum(e["turns"] for e in completed),idle_tail_seconds=tail_time,
                  idle_tail_turns_per_second=sum(e["turns"] for e in completed)/tail_time,
                  completed_idle_games=len(completed), outcome_labels=0,
                  note="Observed rate includes JSON and Python IPC. Separate idle-tail rate omits intermediate observations. No training labels saved.")
    save("stage1-throughput.json", result)
    return result


def check_calibration(games, panel, maps, ratings, noise_pair, handicaps):
    expected={(a,b,m) for a in panel.values() for b in panel.values() for m in maps}
    actual=[(g["a"],g["b"],g["map"]) for g in games]
    if len(actual)!=len(expected) or set(actual)!=expected:
        raise ValueError("Calibration schedule is incomplete or duplicated")
    for game in games:
        if game.get("outcome") not in ("teamA","teamB") or game.get("error"):
            raise ValueError("Incomplete calibration game")
        if any(t["faults"] or t["fuel_exhausted"] for t in game["teams"].values()):
            raise ValueError("Calibration bot fault or fuel exhaustion")
    starter,seed=noise_pair
    gap=abs(ratings[starter]-ratings[seed])
    handicap_gaps={name:ratings[starter]-ratings[name] for name in handicaps}
    if any(v<=0 for v in handicap_gaps.values()) or gap>=min(handicap_gaps.values()):
        raise ValueError("Calibration does not resolve the handicap controls above the seed noise")
    return dict(games=len(games),maps=len(maps),faults=0,fuel_exhausted=0,
                ratings=ratings,seed_gap=gap,handicap_gaps=handicap_gaps)


def calibrate():
    cfg=core.config();panel=cfg["league"]["panel"]
    pairs=[(a,b) for i,a in enumerate(panel) for b in panel[i:]]
    games=core.play(pairs,cfg["maps"]["screen"],cfg["stage1"]["jobs"])
    text,summary=report.build(games,"Stage 1 calibration (generated screen maps)",cfg)
    versions={name:core.version(name).meta["wasm_sha256"] for name in panel}
    audit=check_calibration(games,versions,cfg["maps"]["screen"],summary["ratings"],
                            cfg["league"]["noise_pair"],cfg["stage1"]["handicaps"])
    manifest=json.loads((core.ROOT/"mechanics/generated-maps-g1.json").read_text())
    audit.update(schema=1,passed=True,panel=versions,runtime=core.runtime_identity(),
                 map_manifest_sha256=json_sha(core.ROOT/"mechanics/generated-maps-g1.json"),
                 generated_holdouts=len([m for m in manifest["maps"] if "/confirm/" in m["path"]]),
                 records_sha256=hashlib.sha256(json.dumps(sorted(games,key=lambda g:g["key"]),sort_keys=True).encode()).hexdigest())
    (core.ROOT/"results/calibration-generated-g1.md").write_text(text,encoding="utf-8")
    save("stage1-calibration.json",audit)
    return audit


def require_proof(proof,current):
    if proof.get("passed") is not True: raise ValueError("Stage 1 proof failed")
    if proof.get("sources")!=current: raise ValueError("Stage 1 proof is stale; rerun its check")


def ready():
    current=sources()
    proofs={name:json.loads((core.ROOT/"results"/f"stage1-{name}.json").read_text())
            for name in ("parity","throughput","calibration")}
    for proof in proofs.values(): require_proof(proof,current)
    if proofs["parity"]["runtime"]!=core.runtime_identity(): raise ValueError("Runtime changed since parity proof")
    digest=core.sha(mapgen.engine_path())
    if any(p["engine_wasm_sha256"]!=digest for p in (proofs["parity"],proofs["throughput"])):
        raise ValueError("Rules module changed")
    manifest_path=core.ROOT/"mechanics/generated-maps-g1.json"
    if json_sha(manifest_path)!=proofs["calibration"]["map_manifest_sha256"]:raise ValueError("Map manifest changed")
    manifest=json.loads(manifest_path.read_text())
    for row in manifest["maps"]:
        if core.sha(core.ROOT/row["path"])!=row["sha256"]:raise ValueError("Generated map changed")
    for name,sha in proofs["calibration"]["panel"].items():
        if core.sha(core.version(name).wasm)!=sha:raise ValueError("Frozen calibration bytes changed")
    if proofs["throughput"]["actor_turns_per_second"]<core.config()["stage1"]["min_observed_turns_per_second"]:
        raise ValueError("Actor observation throughput is below the declared floor")
    result=dict(schema=1,passed=True,stage=1,next_stage=2,
                observations=sum(m["observations"] for m in proofs["parity"]["maps"]),
                release_games=proofs["calibration"]["games"],generated_maps=len(manifest["maps"]),
                kernel_fuel_max=max(m["kernel_fuel_max"] for m in proofs["parity"]["maps"]),
                actor_turns_per_second=proofs["throughput"]["actor_turns_per_second"],
                stage2_dataset_started=(core.ROOT/'results/stage2-dataset.json').exists())
    save("stage1-ready.json",result)
    return result
