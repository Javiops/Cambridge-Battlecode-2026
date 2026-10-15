"""Geometry-based held-camp re-entry policies, independent of map fingerprints.

Apply before other micro transforms or after a corners component. These only
filter travel-target selection: the existing committed-camp flow and capture
execution remain untouched. No buddy can be guaranteed reachable through walls;
the support test is an explicitly limited Chebyshev-distance heuristic.
"""
from __future__ import annotations

FEATURES = ("reentry16", "reentry32")

HELPERS = r'''
// Cache only currently available nearby support, once per target decision.
// An out-of-vision ally must not abort inspection of the remaining roster.
std::vector<vec2> held_reentry_buddies(State& s, bc::champion& me, vec2 pos) {
    std::vector<vec2> result;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            try {
                if (a == me || !a.is_alive()) continue;
                const vec2 p = a.position();
                if (dist(p, pos) > 6) continue;
                const double hp = a.health(), mhp = std::max(1.0, static_cast<double>(a.max_health()));
                if (hp < 0.35 * mhp || (s.my_spawn.is_set(p) && hp < 0.95 * mhp)) continue;
                if (a.is_recalling() || a.is_teleporting() || a.is_submitting_gems()) continue;
                result.push_back(p);
            } catch (...) {
            }
        }
        return true;
    });
    return result;
}

bool held_reentry_has_buddy(vec2 pos, vec2 camp, const std::vector<vec2>& buddies) {
    const int limit = dist(pos, camp) + 2;
    for (auto p : buddies)
        if (dist(p, camp) <= limit) return true;
    return false;
}

'''


def _replace_once(text,old,new):
    if text.count(old)!=1:
        raise ValueError(f"Expected one study27 anchor: {old[:100]!r}")
    return text.replace(old,new,1)


def apply(source:dict[str,str],feature:str)->dict[str,str]:
    if feature not in FEATURES:raise ValueError(feature)
    out=dict(source)
    main=out["main.cpp"]
    if "held_reentry_buddies("in main:raise ValueError("Re-entry policy already present")
    window=int(feature.removeprefix("reentry"))
    main=_replace_once(main,"int choose_target(State& s, bc::champion& me, int round) {\n",
                       HELPERS+"int choose_target(State& s, bc::champion& me, int round) {\n")
    # This complete function-prefix anchor survives corners source transforms.
    main=_replace_once(main,"int choose_target(State& s, bc::champion& me, int round) {\n    auto sm = read_sm();\n    vec2 pos = me.position();\n    double hp = me.health();\n",
        "int choose_target(State& s, bc::champion& me, int round) {\n    auto sm = read_sm();\n    vec2 pos = me.position();\n"
        f"    const bool reentry_danger_recent = P_HOLD && P_DANGER && round >= s.danger_r && round - s.danger_r <= {window};\n"
        "    const auto reentry_buddies_cache = reentry_danger_recent ? held_reentry_buddies(s, me, pos) : std::vector<vec2>{};\n"
        "    double hp = me.health();\n")
    main=_replace_once(main,"        bool held = P_HOLD && s.hold_group[i];\n",
        "        bool held = P_HOLD && s.hold_group[i];\n"
        "        // Apply to held geometry on every map; never veto a known fresh reward.\n"
        "        if (held && reentry_danger_recent && dist(g.center, s.danger_p) <= P_DANGER_R &&\n"
        "            !(g.reward_seen >= 0 && round - g.reward_seen < 30) &&\n"
        "            !held_reentry_has_buddy(pos, g.center, reentry_buddies_cache)) continue;\n")
    out["main.cpp"]=main
    return out


def _contracts():
    """Optional local source and actual-C++ helper checks; no matches."""
    import hashlib
    import importlib.util
    import json
    from pathlib import Path
    import subprocess
    root=Path(__file__).resolve().parent
    base={p.name:p.read_text()for p in(root/"baseline/src").iterdir()if p.is_file()}
    before=dict(base)
    # Import the existing fixture utility only in this optional test entry.
    spec=importlib.util.spec_from_file_location("study27_farm_fixture",root/"test_farm_helper.py")
    first=importlib.util.module_from_spec(spec);spec.loader.exec_module(first)
    changed={name:apply(base,name)for name in FEATURES}
    assert base==before
    for name,files in changed.items():
        assert {k for k in base if base[k]!=files[k]}=={"main.cpp"}
        text=files["main.cpp"]
        assert "v34de::Corners"not in HELPERS
        old_danger="        if (!held && P_DANGER && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R) continue;"
        assert text.count(old_danger)==base["main.cpp"].count(old_danger)==1
        for start,end in (("void farm(","// ---------------------------------------------------------------------------\n// One turn"),
                         ("bool other_captures(","void drop_target("),
                         ("    // 2. Badly hurt:","    // 3."),
                         ("    // 4. Recall to heal","    // 5. Bank gems.")):
            cut=lambda s:s.split(start,1)[1].split(end,1)[0]
            assert cut(text)==cut(base["main.cpp"]),(name,start)
        try:apply(files,name)
        except ValueError:pass
        else:raise AssertionError("Repeated policy accepted")
    records=[]
    prefix=first.PREFIX.replace("Mask en_spawn,blocked;","Mask en_spawn,blocked,my_spawn;int danger_r=-1000;vec2 danger_p{15,10};")
    extra=r'''
#define P_HOLD 200
#define P_DANGER 3
#define P_DANGER_R 6
struct Group {vec2 center{15,10};int reward_seen=-1;};
'''
    cases=r'''
int main() {
    int checks=0;auto test=[&](bool pass){assert(pass);++checks;};
    reset();State s;bc::champion me;const vec2 pos=me.position();
    test(held_reentry_buddies(s,me,pos).empty());
    bc::vision::allies={me};test(held_reentry_buddies(s,me,pos).empty());
    auto ally=foe(3,11,10).c;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).size()==1);
    ally.hp=349;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).empty());
    ally.hp=350;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).size()==1);
    s.my_spawn.tiles={ally.p};test(held_reentry_buddies(s,me,pos).empty());
    ally.hp=950;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).size()==1);
    s.my_spawn.tiles.clear();ally.recall=true;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).empty());
    ally.recall=false;ally.teleport=true;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).empty());
    ally.teleport=false;ally.submit=true;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).empty());
    ally.submit=false;ally.p={16,10};bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).size()==1);
    ally.p={17,10};bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).empty());
    ally.p={11,10};auto hidden=ally;hidden.bad=true;hidden.id=4;bc::vision::allies={hidden,ally};
    test(held_reentry_buddies(s,me,pos).size()==1);
    ally.alive=false;bc::vision::allies={ally};test(held_reentry_buddies(s,me,pos).empty());
    test(!held_reentry_has_buddy(pos,{15,10},{}));
    test(held_reentry_has_buddy(pos,{15,10},{{8,10}}));
    test(!held_reentry_has_buddy(pos,{15,10},{{7,10}}));
    s.danger_r=100;Group g;
    test(!select(s,g,true,100,{}));
    test(!select(s,g,true,100+@WINDOW@,{}));
    test(select(s,g,true,101+@WINDOW@,{}));
    test(select(s,g,true,99,{}));
    test(select(s,g,false,100,{}));
    test(select(s,g,true,100,{{11,10}}));
    test(!select(s,g,true,100,{{7,10}}));
    g.reward_seen=100;test(select(s,g,true,100,{}));
    s.danger_r=129;test(select(s,g,true,129,{}));
    s.danger_r=130;test(!select(s,g,true,130,{}));
    g.reward_seen=-1;g.center={22,10};s.danger_r=100;test(select(s,g,true,100,{}));
    std::printf("actual held reentry helpers/selection: %d checks passed\n",checks);
}
'''
    for name,files in changed.items():
        text=files["main.cpp"]
        helper1=first.block(text,"std::vector<vec2> held_reentry_buddies(")
        helper2=first.block(text,"bool held_reentry_has_buddy(")
        recent=next(line for line in text.splitlines()if "const bool reentry_danger_recent ="in line)
        guard_start=text.index("        if (held && reentry_danger_recent")
        guard_end=text.index("continue;",guard_start)+len("continue;")
        selection="bool select(State& s,Group& g,bool held,int round,const std::vector<vec2>& reentry_buddies_cache){\nvec2 pos{10,10};\n"+recent+"\nfor(int i=0;i<1;++i){\n"+text[guard_start:guard_end]+"\nreturn true;\n}return false;\n}\n"
        code=prefix+first.block(base["main.cpp"],"struct Threat {")+";\n"+first.MIDDLE+extra+helper1+helper2+selection+cases.replace("@WINDOW@",name.removeprefix("reentry"))
        cpp,wasm=root/f"fixture-{name}.cpp",root/f"fixture-{name}.wasm"
        cpp.write_text(code,newline="\n")
        proc=subprocess.run([str(first.COMPILER),"-std=c++20","-fwasm-exceptions","-O2",str(cpp),"-lunwind","-o",str(wasm)],capture_output=True,text=True)
        if proc.returncode:raise RuntimeError(proc.stderr)
        runner=root/f"fixture-{name}.mjs"
        runner.write_text(f'''import fs from 'node:fs';
import {{WASI}} from 'node:wasi';
const wasi=new WASI({{version:'preview1',args:[],env:{{}},preopens:{{}}}});
const {{instance}}=await WebAssembly.instantiate(fs.readFileSync(new URL('./{wasm.name}',import.meta.url)),{{wasi_snapshot_preview1:wasi.wasiImport}});
wasi.start(instance);
''',newline="\n")
        proc=subprocess.run([str(first.NODE),str(runner)],capture_output=True,text=True)
        if proc.returncode:raise RuntimeError(proc.stdout+proc.stderr)
        records.append({"feature":name,"stdout":proc.stdout.strip(),"cpp_sha256":hashlib.sha256(cpp.read_bytes()).hexdigest()})
    output={"passed":True,"source_contracts":2,"method":"Actual inserted C++ helpers and held-selection clause extracted, WASI-compiled and executed against narrow SDK stand-ins. No engine games.","fixtures":records,
            "patch_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (root/"reentry-fixtures.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))


if __name__=="__main__":_contracts()
