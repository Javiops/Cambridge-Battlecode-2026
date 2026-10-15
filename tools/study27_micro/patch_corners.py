"""Reconstruct verified team v39 corners source and its component ablations.

apply() is self-contained: it needs only a source dictionary from pinned
study27/c462346d. No source or patch file is loaded at transformation time.
The optional script entry point validates against the archived local sources.
"""
from __future__ import annotations
import hashlib

COMPONENTS = {
    "corners_lone": (True,False,False),
    "corners_reentry": (False,True,False),
    "corners_flee": (False,False,True),
    "corners_lone_reentry": (True,True,False),
    "corners_lone_flee": (True,False,True),
    "corners_reentry_flee": (False,True,True),
    "corners_v39": (True,True,True),
}
FEATURES = tuple(COMPONENTS)
BASE_PINS = {
    "main.cpp":"0650eda916f8f2fe16ae69923d239d15e916e738205e90060113fac65a85453f",
    "params.h":"5cc4bcda14dde61df979267dd5485abd89753f2d8b27f7e5b98ba3b0496ddda8",
}

DEFINES = '''// P_CRN (corners only, 2026-10-15 corners study: 35% of our deaths were a champion back from spawn walking alone
// into their pack at the held centre; ours drop below 35% hp 3 tiles from a foe and 63% die):
//   no centre hold on corners (camps obey the shared danger spot), a danger camp is allowed again only with
//   P_CRN_BUDDY allies within 6 (go back together), and leave the fight below P_CRN_FLEE % hp.
// P_MITE (every other map, the #1 Mite's survival rule): no centre hold, leave below P_MITE_FLEE % hp and recall
//   once the nearest foe is P_MITE_RNEAR tiles away (Mite: under 50%, walks out to 7 and recalls, 93% finish).
#ifndef P_CRN
#define P_CRN 0
#endif
#ifndef P_CRN_NOHOLD
#define P_CRN_NOHOLD 1
#endif
#ifndef P_CRN_LONE
#define P_CRN_LONE 0  // corners with the hold kept: a held camp near a pack seen in the last N rounds needs P_CRN_BUDDY allies within 6
#endif
#ifndef P_CRN_FLEE
#define P_CRN_FLEE 55
#endif
#ifndef P_CRN_BUDDY
#define P_CRN_BUDDY 2
#endif
#ifndef P_MITE
#define P_MITE 0
#endif
#ifndef P_MITE_NOHOLD
#define P_MITE_NOHOLD 1
#endif
#ifndef P_MITE_FLEE
#define P_MITE_FLEE 50
#endif
#ifndef P_MITE_RNEAR
#define P_MITE_RNEAR 7
#endif
'''

FLEE_HELPER = '''// Leave-the-fight line in % hp: P_CRN on corners, P_MITE elsewhere, else P_UNI_FLEE (caster draft) or flee_pct.
int flee_line(const State& s) {
    if (P_CRN && s.de_map == v34de::Corners) return P_CRN_FLEE;
    if (P_MITE && P_MITE_FLEE && s.de_map != v34de::Corners) return P_MITE_FLEE;
    return (P_UNI_FLEE && P_DRAFTUNI && s.casters) ? P_UNI_FLEE : P.flee_pct;
}

'''

INIT_BLOCK = '''    attempt([&] {
        bool crn = P_CRN && P_CRN_NOHOLD && s.de_map == v34de::Corners, mite = P_MITE && s.de_map != v34de::Corners;
        if (crn || (mite && P_MITE_NOHOLD)) {
            s.hold = -1;
            s.hold_group.assign(s.groups.size(), 0);
        }
        if (mite && P_MITE_RNEAR) s.rnear = P_MITE_RNEAR;
        return true;
    });
'''

BUDDY_BLOCK = '''    // P_CRN: on corners a danger camp is fine again when we walk in with P_CRN_BUDDY allies within 6
    int buddies = 0, crn_buddy = (P_CRN && s.de_map == v34de::Corners) ? P_CRN_BUDDY : 1 << 20;
    if (crn_buddy < (1 << 20))
        attempt([&] {
            for (auto& a : bc::vision::champions(*s.my))
                if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ++buddies;
            return true;
        });
'''

BASE_DANGER = "        if (!held && P_DANGER && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R) continue;\n"
V39_DANGER = "        if (!held && P_DANGER && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R && buddies < crn_buddy) continue;\n"
LONE_LINE = "        if (held && P_CRN_LONE && crn_buddy < (1 << 20) && round - s.danger_r <= P_CRN_LONE && dist(g.center, s.danger_p) <= P_DANGER_R && buddies < crn_buddy) continue;\n"
BASE_FLEE = "if (hpr * 100 < ((P_UNI_FLEE && P_DRAFTUNI && s.casters) ? P_UNI_FLEE : P.flee_pct)) {"
V39_FLEE = "if (hpr * 100 < flee_line(s)) {"
PARAMS = "\n#define P_CRN 1\n#define P_CRN_NOHOLD 0\n#define P_CRN_LONE 16\n#define P_CRN_BUDDY 1\n#define P_CRN_FLEE 45\n"


def _replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one pinned study27 anchor: {old[:100]!r}")
    return text.replace(old,new,1)


def apply(source: dict[str,str], feature: str) -> dict[str,str]:
    if feature not in FEATURES:
        raise ValueError(feature)
    # Normalise line endings only; bytes otherwise stay exactly as supplied.
    out = {k:v.replace("\r\n","\n") for k,v in source.items()}
    for name,expected in BASE_PINS.items():
        if hashlib.sha256(out[name].encode("utf-8")).hexdigest() != expected:
            raise ValueError("Not pinned c462346d study27: "+name)
    main = out["main.cpp"]
    main = _replace_once(main,"#ifndef P_UNI_FLEE\n",DEFINES+"#ifndef P_UNI_FLEE\n")
    main = _replace_once(main,"void init(State& s, bc::champion& me) {\n",FLEE_HELPER+"void init(State& s, bc::champion& me) {\n")
    main = _replace_once(main,"\n    attempt([&] {\n        build_shop(s, me);\n", INIT_BLOCK+"\n    attempt([&] {\n        build_shop(s, me);\n")
    main = _replace_once(main,"    bool have_pd = P_PATHD && attempt([&] {",BUDDY_BLOCK+"    bool have_pd = P_PATHD && attempt([&] {")
    main = _replace_once(main,BASE_DANGER,V39_DANGER+LONE_LINE)
    if main.count(BASE_FLEE) != 2:
        raise ValueError("Expected both pinned flee threshold conditions")
    main = main.replace(BASE_FLEE,V39_FLEE)
    out["params.h"] += PARAMS
    lone,reentry,flee = COMPONENTS[feature]
    if not flee:
        # Keep the exact original flee rule, including its caster/noncaster
        # distinction. Setting P_CRN_FLEE=0 would incorrectly disable fleeing.
        main = main.replace(V39_FLEE,BASE_FLEE)
    if not reentry:
        # A buddy relaxing the nonheld-camp danger exclusion is independent
        # from the held-camp lone-entry restriction. Ablate both separately.
        main = _replace_once(main,V39_DANGER,BASE_DANGER)
    if not lone:
        main = _replace_once(main,LONE_LINE,"")
        out["params.h"] = _replace_once(out["params.h"],"#define P_CRN_LONE 16\n","#define P_CRN_LONE 0\n")
    if not lone and not reentry:
        main = _replace_once(main,BUDDY_BLOCK,"")
    out["main.cpp"] = main
    return out


def _check_local():
    """Optional development contract; apply() itself never reads local files."""
    import json
    from pathlib import Path
    root=Path(__file__).resolve().parent
    base={p.name:p.read_text()for p in (root/"baseline/src").iterdir()if p.is_file()}
    actual={p.name:p.read_text()for p in (root/"corners-baseline/src").iterdir()if p.is_file()}
    before=dict(base)
    full=apply(base,"corners_v39")
    assert base==before and full==actual,"Full v39 must reproduce all six normalised source files exactly"
    lone_reentry,flee=apply(base,"corners_lone_reentry"),apply(base,"corners_flee")
    assert {k for k in base if full[k]!=base[k]}=={"main.cpp","params.h"}
    assert lone_reentry["main.cpp"].count(BASE_FLEE)==2 and V39_FLEE not in lone_reentry["main.cpp"]
    start,end="int choose_target(","std::optional<vec2> best_altar("
    cut=lambda s:s.split(start,1)[1].split(end,1)[0]
    assert cut(flee["main.cpp"])==cut(base["main.cpp"]),"Flee-only must retain exactly original camp selection"
    assert cut(lone_reentry["main.cpp"])==cut(full["main.cpp"])
    assert BUDDY_BLOCK not in flee["main.cpp"] and LONE_LINE not in flee["main.cpp"]
    assert "#define P_CRN_NOHOLD 0\n"in full["params.h"] and "#define P_MITE 0\n"in full["main.cpp"]
    for name in FEATURES:
        v=apply(base,name)
        l,r,f=COMPONENTS[name]
        assert (LONE_LINE in v["main.cpp"])==l,(name,"held guard")
        assert (V39_DANGER in v["main.cpp"])==r,(name,"nonheld buddy reentry")
        assert (BASE_DANGER in v["main.cpp"])==(not r),(name,"original nonheld condition")
        assert (BUDDY_BLOCK in v["main.cpp"])==(l or r),(name,"buddy scan")
        assert v["main.cpp"].count(V39_FLEE)==(2 if f else 0),(name,"flee conditions")
        assert v["main.cpp"].count(BASE_FLEE)==(0 if f else 2),(name,"original flee conditions")
        for begin,end in (("bool other_captures(","void drop_target("),
                ("// Nothing of this group is visible alive.","// ---------------------------------------------------------------------------\n// One turn"),
                ("    // 4. Recall to heal","    // 5. Bank gems.")):
            section=lambda s:s.split(begin,1)[1].split(end,1)[0]
            assert section(v["main.cpp"])==section(base["main.cpp"]),(name,"capture/recall preservation")
        assert all(v[k]==base[k]for k in base if k not in("main.cpp","params.h"))
        try:apply(v,name)
        except ValueError:pass
        else:raise AssertionError("Repeated transform accepted: "+name)
    print(json.dumps({"passed":True,"full_v39_exact_normalised_source":True,"components":FEATURES,
                      "source_sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in full.items()},
                      "component_bits_lone_reentry_flee":COMPONENTS,
                      "patch_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))


if __name__=="__main__":_check_local()
