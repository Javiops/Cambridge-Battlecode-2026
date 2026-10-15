"""Narrow follow-up study27 farming policies; frozen first-stage patch is untouched.

These are development adaptations after the broad guards lost to the spar panel,
not an independent confirmation. Each feature is an independent source transform.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

FEATURES = ("start_only_backoff", "start_only_retarget", "no_contact_dash",
            "reserve_cc_contact5", "reserve_cc_contact3")

CONTACT_HELPER = r'''
// Contact is local to this champion or the camp it is about to hit. Distant
// visible foes and channels do not justify changing otherwise productive farm.
bool farm_contact(State& s, bc::champion& me, vec2 camp, const std::vector<Foe>& foes,
                  int self_radius, int camp_radius, bool healthy_only = false) {
    if (foes.empty()) return false;
    const vec2 pos = me.position();
    for (const auto& f : foes) {
        bool contact = attempt([&] {
            const auto& c = f.c;
            if (!c.is_visible() || !c.is_alive()) return false;
            const vec2 p = c.position();
            if (s.en_spawn.is_set(p) ||
                (dist(p, pos) > self_radius && dist(p, camp) > camp_radius)) return false;
            if (c.is_recalling() || c.is_teleporting() || c.is_submitting_gems()) return false;
            return !healthy_only || c.health() >= 0.35f * c.max_health();
        });
        if (contact) return true;
    }
    return false;
}

'''


def _replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected exactly one study27 anchor: {old[:100]!r}")
    return text.replace(old, new, 1)


def _old_patch():
    path = Path(__file__).with_name("patch_farm.py")
    spec = importlib.util.spec_from_file_location("study27_frozen_farm_patch", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply(source: dict[str, str], feature: str) -> dict[str, str]:
    if feature not in FEATURES:
        raise ValueError(feature)
    out = dict(source)
    if feature in ("start_only_backoff", "start_only_retarget"):
        out = _old_patch().apply(out, "farm_outnumbered_backoff")
        main = _replace_once(out["main.cpp"],
            "        if (farm_under_threat(s, me, *tgt, str, foes)) {\n",
            "        // Avoid starting an outnumbered camp, without abandoning an already damaged one.\n"
            "        if (!engaged && farm_under_threat(s, me, *tgt, str, foes)) {\n")
        if feature == "start_only_retarget":
            main = _replace_once(main,
                '            g_farm = "threat-backoff";\n            fight::back_off(s, me, foes, round);',
                '            g_farm = "threat-retarget";\n'
                "            g.bad_until = round + 8;\n"
                "            drop_target(s);\n"
                "            fight::back_off(s, me, foes, round);")
        out["main.cpp"] = main
        return out

    main = out["main.cpp"]
    main = _replace_once(main,
        "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {",
        CONTACT_HELPER + "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps, const std::vector<Foe>& foes) {")
    main = _replace_once(main, "    farm(s, me, round, camps);\n", "    farm(s, me, round, camps, foes);\n")
    if feature == "no_contact_dash":
        main = _replace_once(main,
            "        engage(s, me, *tgt, tgt->position(), false, true);\n",
            "        // Preserve a dash near a healthy enemy; spells, basics and ordinary walking stay available.\n"
            "        const bool save_dash = s.dash_slot >= 0 && farm_contact(s, me, tgt->position(), foes, 6, 5, true);\n"
            "        engage(s, me, *tgt, tgt->position(), false, !save_dash);\n")
    else:
        radius = int(feature[-1])
        main = _replace_once(main, "struct State {\n    bool ready = false;\n",
            "struct State {\n    bool ready = false;\n    bool farm_preserve_cc = false;\n")
        # This gate only affects camp casts. Enemy champion casts and attack
        # resets use their existing paths and remain unchanged.
        main = _replace_once(main,
            "        // P_SAVECC: keep stuns for champions while enemies were seen in the last P_SAVECC rounds.\n",
            "        if (!champ && s.farm_preserve_cc && attempt([&] { return ab.is_cc(); })) continue;\n"
            "        // P_SAVECC: keep stuns for champions while enemies were seen in the last P_SAVECC rounds.\n")
        main = _replace_once(main,
            "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps, const std::vector<Foe>& foes) {\n",
            "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps, const std::vector<Foe>& foes) {\n"
            "    s.farm_preserve_cc = false;\n")
        main = _replace_once(main,
            "        engage(s, me, *tgt, tgt->position(), false, true);\n",
            "        // Keep CC for current nearby enemy contact, not for a last-seen timer.\n"
            f"        s.farm_preserve_cc = farm_contact(s, me, tgt->position(), foes, {radius}, {radius});\n"
            "        engage(s, me, *tgt, tgt->position(), false, true);\n")
    out["main.cpp"] = main
    return out
