"""Independent study27 live-camp farming guards.

These transforms never mutate their input, shared-memory layout, draft, recall,
capture handling, or the generic engage/pathfinding implementation. They only
decide whether the last live-camp engage is worth committing this turn. The
advance envelope deliberately overapproximates legal one-step / dash-and-step
camp-closing landings; it is a heuristic, not a path or combat proof.
"""
from __future__ import annotations

MODES = ("outnumbered", "volley", "contested")
RESPONSES = ("hold", "backoff")
GUARDS = tuple(f"farm_{mode}_{response}" for mode in MODES for response in RESPONSES)
RESERVES = ("reserve_cc3", "reserve_cc6")
FEATURES = GUARDS + RESERVES

HELPER = r'''
// The live camp branch is reached after existing champion-fight, banking and
// recall decisions. Do not spend camp cooldowns or advance into an unfavourable
// nearby threat; ready rewards continue through the unchanged capture branch.
bool farm_under_threat(State& s, bc::champion& me, const bc::camp& camp,
                       double camp_strength, const std::vector<Foe>& foes) {
    ++s.farm_guard_checks;
    if (foes.empty() || !fuel_ok(22000)) return false;
    const vec2 pos = me.position(), cp = camp.position();
    const double hp = me.health();
    const int camp_dist = dist(pos, cp), ar = static_cast<int>(me.attack_range());
    int advance = me.can_move() ? 1 : 0;
    // step_towards may dash two tiles and then take its normal one-tile step.
    if (s.dash_slot >= 0 && me.can_cast() &&
        attempt([&] { return me.abilities()[s.dash_slot].is_ready(); })) advance = 3;
    if (camp_dist > ar + advance + 1) return false;

    std::vector<Foe> local;
    std::vector<Threat> threats;
    for (auto f : foes) {
        try {
            if (!f.c.is_visible() || !f.c.is_alive()) continue;
            f.p = f.c.position();
            if (s.en_spawn.is_set(f.p) || dist(f.p, pos) > 9 ||
                f.c.is_recalling() || f.c.is_teleporting() || f.c.is_submitting_gems()) continue;
            f.hp = f.c.health();
            f.d = dist(f.p, pos);
            local.push_back(f);
            // Existing spell model reads cooldown(), not per-turn can_cast().
            // Basic reach is next-turn range, including known melee dashes.
            threats.push_back(threat_of(f.c, f.p, fight::reach(f)));
        } catch (...) {
        }
    }
    if (local.empty()) return false;

    struct FarmMate { vec2 p; double hp; Threat damage; };
    std::vector<FarmMate> mates;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            try {
                if (a == me || !a.is_alive() || a.health() < 0.35f * a.max_health() ||
                    a.is_recalling() || a.is_teleporting() || a.is_submitting_gems()) continue;
                vec2 p = a.position();
                if (dist(p, pos) > 8) continue;
                // Count a normal step plus basic range, not a hypothetical
                // ally dash whose cooldown/availability was never checked.
                const int help_reach = static_cast<int>(a.attack_range()) + 1;
                mates.push_back({p, a.health(), threat_of(a, p, help_reach)});
            } catch (...) {
            }
        }
        return true;
    });

    auto threatened = [&](vec2 tile) {
        int enemy_bodies = 0, ours = 1;
        double enemy_hp = 0, our_hp = hp;
        std::vector<std::size_t> active;
        for (std::size_t i = 0; i < local.size(); ++i) {
            const auto& th = threats[i];
            const int d = dist(tile, th.p);
            if (d > th.ar && d > th.xr && d > th.fr + 1 && d > th.sr + 1) continue;
            ++enemy_bodies;
            enemy_hp += local[i].hp;
            active.push_back(i);
        }
        if (!enemy_bodies) return false;
        // An ally eight tiles away may inflate the old fight's health total but
        // cannot protect this camp. Count it only if its ready reach touches a
        // threatening enemy; channeling and badly hurt allies were excluded.
        for (const auto& ally : mates) {
            bool helps = false;
            for (auto i : active) {
                const int d = dist(ally.p, local[i].p);
                const auto& th = ally.damage;
                if (d <= th.ar || d <= th.xr || d <= th.fr + 1 || d <= th.sr + 1) {
                    helps = true;
                    break;
                }
            }
            if (helps) { ++ours; our_hp += ally.hp; }
        }
        const double volley = danger_at(threats, tile);
        const bool outnumbered = enemy_bodies > ours;
        if (@MODE@ == 1) return outnumbered;
        // Monster strength is an upper-bound raw-hit estimate, not measured
        // post-armour damage. It matters only when a champion can also hit us.
        const double pressure = volley + (dist(tile, cp) <= CAMP_RANGE ? camp_strength : 0.0);
        const bool no_advantage = enemy_hp >= 0.85 * our_hp;
        if (@MODE@ == 2)
            return outnumbered || (pressure >= 0.35 * hp && no_advantage);
        // A stronger contested-camp rule: spending a large fraction of health
        // while the other side is still competitive risks both fight and loot.
        return outnumbered || (pressure >= 0.20 * hp && no_advantage);
    };

    bool unsafe = threatened(pos);
    if (!unsafe && camp_dist > ar && advance > 0) {
        // Any legal camp-closing landing can be selected by the existing path
        // planner, including a dash and follow-up step. Use a conservative
        // envelope instead of claiming to predict an exact path through walls.
        for (int dx = -advance; dx <= advance && !unsafe; ++dx)
            for (int dy = -advance; dy <= advance && !unsafe; ++dy) {
                if (!fuel_ok(12000)) return false;
                if (!dx && !dy) continue;
                vec2 tile = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(tile) || s.blocked.is_set(tile) ||
                    dist(tile, cp) >= camp_dist) continue;
                unsafe = threatened(tile);
            }
    }
    if (unsafe) ++s.farm_guard_blocks;
    return unsafe;
}

'''


def _replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected exactly one study27 anchor: {old[:100]!r}")
    return text.replace(old, new, 1)


def apply(source: dict[str, str], feature: str | None = None, *,
          mode: str = "outnumbered", response: str = "hold") -> dict[str, str]:
    """Return one complete candidate source; a feature name takes precedence."""
    if feature in RESERVES:
        out = dict(source)
        # The existing cast_offense gate preserves CC spells on live camps for
        # this many rounds after seeing a foe. It does not preserve resets or
        # ordinary damage-only spells, and never changes champion casting.
        out["params.h"] += ("\n// Preserve crowd-control cooldowns for nearby champion contact.\n"
                            f"#define P_SAVECC {feature[-1]}\n")
        return out
    if feature is not None:
        if feature not in GUARDS:
            raise ValueError(f"Unknown feature: {feature}")
        mode, response = feature.removeprefix("farm_").rsplit("_", 1)
    if mode not in MODES or response not in RESPONSES:
        raise ValueError((mode, response))
    out = dict(source)
    main = out["main.cpp"]
    main = _replace_once(main, "struct State {\n    bool ready = false;\n", "struct State {\n    bool ready = false;\n    int farm_guard_checks = 0, farm_guard_blocks = 0;\n")
    main = _replace_once(main,
        "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {",
        HELPER.replace("@MODE@", str(MODES.index(mode) + 1)) +
        "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps, const std::vector<Foe>& foes) {")
    action = ("shoot_back(s, me, foes);" if response == "hold" else
              "fight::back_off(s, me, foes, round);")
    main = _replace_once(main,
        "        engage(s, me, *tgt, tgt->position(), false, true);\n",
        "        if (farm_under_threat(s, me, *tgt, str, foes)) {\n"
        f'            g_farm = "threat-{response}";\n'
        f"            {action}\n"
        "            return;\n"
        "        }\n"
        "        engage(s, me, *tgt, tgt->position(), false, true);\n")
    main = _replace_once(main, "    farm(s, me, round, camps);\n", "    farm(s, me, round, camps, foes);\n")
    main = _replace_once(main,
        "                    static_cast<unsigned long long>(bc::fuel_remaining()));\n        std::fflush(stdout);",
        "                    static_cast<unsigned long long>(bc::fuel_remaining()));\n"
        "        if (s.farm_guard_blocks)\n"
        '            std::printf("[farmguard] r=%d checks=%d blocks=%d\\n", round, s.farm_guard_checks, s.farm_guard_blocks);\n'
        "        std::fflush(stdout);")
    out["main.cpp"] = main
    return out
