"""Composable camp-combat/loot experiments on the cleaned PR11 baseline.

Transforms are source-only and read no local files. The focus forecast is a
policy heuristic, not an engine target/path/timing proof. No recall, draft,
shopping or shared-memory-layout changes. No games are run by this module.
"""
from __future__ import annotations

FEATURES = ("cf_camp_reach", "cf_camp_focus", "cf_camp_evac")

FIELDS = r'''
    unsigned cf_reach = 0, cf_focus_wait = 0, cf_focus_exit = 0, cf_focus_hit = 0, cf_evac = 0;
    unsigned cf_reward_gain_observed = 0, cf_death_after_camp = 0;
    int cf_recent_camp = -1000, cf_log_round = -1000;
    bool cf_was_alive = false;
'''

COMMON = r'''
// Local-only diagnostics: these do not use the eight shared bytes.
// A death after a recent camp action is temporal evidence, not kill attribution.
void cf_observe(State& s, bc::champion& me, int round) {
    const bool alive = me.is_alive();
    if (!alive && s.cf_was_alive && round - s.cf_recent_camp <= 2) ++s.cf_death_after_camp;
    s.cf_was_alive = alive;
    if (round % 50 == 0 && s.cf_log_round != round) {
        s.cf_log_round = round;
        std::printf("[econ] who=%d r=%d cf_reach=%u cf_focus_wait=%u cf_focus_exit=%u cf_focus_hit=%u cf_evac=%u cf_reward_gain_observed=%u cf_death_after_camp=%u\n",
                    s.ally_idx, round, s.cf_reach, s.cf_focus_wait, s.cf_focus_exit, s.cf_focus_hit, s.cf_evac,
                    s.cf_reward_gain_observed, s.cf_death_after_camp);
    }
}

// True only for actual visible, healthy allies who can plausibly remain here.
// No claimed-but-absent champion contributes damage to the focus model.
bool cf_available(const bc::champion& a) {
    return a.is_visible() && a.is_alive() && a.health() > 0 &&
           a.health() >= 0.35 * a.max_health() && !a.is_recalling() &&
           !a.is_teleporting() && !a.is_submitting_gems();
}

'''

FOCUS = r'''
struct CfCamp { vec2 p; double hp, strength; int range; };
struct CfHelper { vec2 p; double hp, maxhp, dps; int range; bool self; };
struct CfForecast { double focused = 0, volley = 0, dps = 0; int helpers = 1; };
int cf_contact_distance(int distance, int range) { return std::max(distance, range); }

// Physical monsters do not chase. Charge a full hit on a nearest-distance tie,
// rather than dividing incoming damage by squad size a second time.
double cf_volley(const std::vector<CfCamp>& camps, const std::vector<CfHelper>& helpers, vec2 pos) {
    double out = 0;
    for (const auto& c : camps) {
        const int mine = dist(pos, c.p);
        if (c.strength <= 0 || mine > c.range) continue;
        bool nearest = true;
        for (const auto& a : helpers)
            if (!a.self && dist(a.p, c.p) < mine) { nearest = false; break; }
        if (nearest) out += c.strength;
    }
    return out;
}

CfForecast cf_forecast(std::vector<CfCamp> camps, const std::vector<CfHelper>& helpers,
                       vec2 pos, vec2 focus) {
    CfForecast out;
    out.helpers = static_cast<int>(helpers.size());
    for (const auto& a : helpers) out.dps += a.dps;
    out.dps = std::max(10.0, out.dps);
    std::stable_sort(camps.begin(), camps.end(), [&](const auto& a, const auto& b) {
        if ((a.p == focus) != (b.p == focus)) return a.p == focus;
        return a.hp < b.hp;
    });
    double clear_hp = 0;
    for (const auto& c : camps) {
        clear_hp += c.hp;
        const int mine = dist(pos, c.p);
        if (c.strength <= 0 || mine > c.range) continue;
        bool nearest = true;
        for (const auto& a : helpers)
            if (!a.self && dist(a.p, c.p) < mine) { nearest = false; break; }
        if (nearest) {
            const double rounds = std::max(0.0, std::ceil(clear_hp / out.dps) - 1.0);
            out.focused += c.strength * rounds;
            out.volley += c.strength;
        }
    }
    return out;
}

std::vector<CfCamp> cf_monsters(const std::vector<const bc::camp*>& live) {
    std::vector<CfCamp> out;
    for (auto* c : live) {
        if (!fuel_ok(11000)) break;
        attempt([&] {
            if (!c->is_visible() || c->health() <= 0) return false;
            out.push_back({c->position(), c->health(), c->strength(), c->attack_range()});
            return true;
        });
    }
    return out;
}

std::vector<CfHelper> cf_helpers(State& s, bc::champion& me, const std::vector<CfCamp>& camps) {
    std::vector<CfHelper> out{{me.position(), me.health(), me.max_health(), my_dps(s, me),
                              static_cast<int>(me.attack_range()), true}};
    for (auto& a : bc::vision::champions(*s.my)) {
        if (!fuel_ok(13000)) break;
        attempt([&] {
            if (a == me || !cf_available(a)) return false;
            const vec2 p = a.position();
            if (s.my_spawn.is_set(p) && a.health() < 0.95 * a.max_health()) return false;
            const int ar = static_cast<int>(a.attack_range());
            int distance = 999;
            for (const auto& c : camps) distance = std::min(distance, dist(p, c.p));
            if (distance > ar + 1) return false;
            // One-step-away help is discounted for the walking turn, especially ranged.
            // Basic strength is actual repeatable damage; generic Focus could
            // invent offense for a healer or a purely defensive spell kit.
            double dps = std::max(10.0, static_cast<double>(a.strength()));
            if (distance > ar) dps *= 0.5;
            out.push_back({p, a.health(), a.max_health(), dps, ar, false});
            return true;
        });
    }
    return out;
}

// Approximate the next camp-contact tile using legal geometry, not a hidden
// target centre occupied by a monster. It is not the pathfinder's exact route.
vec2 cf_contact(State& s, bc::champion& me, vec2 target) {
    const vec2 pos = me.position();
    const int ar = static_cast<int>(me.attack_range());
    if (dist(pos, target) <= ar) return pos;
    int reach = me.can_move() ? 1 : 0;
    if (s.dash_slot >= 0 && me.can_cast() && attempt([&] { return me.abilities()[s.dash_slot].is_ready(); }))
        reach += 2;
    vec2 best = pos;
    int best_d = dist(pos, target), best_step = 999;
    for (int dx = -reach; dx <= reach; ++dx)
        for (int dy = -reach; dy <= reach; ++dy) {
            if (!fuel_ok(10000)) return pos;
            vec2 p = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p)) continue;
            const int d = cf_contact_distance(dist(p, target), ar), step = dist(pos, p);
            if (d < best_d || (d == best_d && step < best_step)) {
                best = p; best_d = d; best_step = step;
            }
        }
    return best;
}

bool cf_focus_safe(State& s, bc::champion& me, const std::vector<const bc::camp*>& live,
                    const bc::camp& target, bool engaged, int round) {
    if (!fuel_ok(24000)) return true; // Unknown/incomplete forecasts keep the original action.
    const auto monsters = cf_monsters(live);
    if (monsters.size() != live.size()) return true;
    const auto helpers = cf_helpers(s, me, monsters);
    if (!fuel_ok(9000)) return true;
    const vec2 pos = me.position(), tp = target.position();
    const vec2 contact = cf_contact(s, me, tp);
    if (!fuel_ok(9000)) return true;
    const auto next = cf_forecast(monsters, helpers, contact, tp);
    const double budget = std::max(0.0, static_cast<double>(me.health()) - me.max_health() * P_BAIL_PCT / 100.0);
    if (next.focused <= budget) return true;
    // Never reject an immediately lethal last-monster basic to avoid future damage.
    if (live.size() == 1 && me.can_attack() && dist(pos, tp) <= me.attack_range() &&
        target.health() <= me.strength()) return true;
    ++s.cf_focus_wait;
    g_farm = "focus-wait";
    const double here = cf_volley(monsters, helpers, pos);
    const double enemy_here = danger_at(s.thr, pos);
    std::optional<vec2> escape;
    double best = here;
    if (me.can_move() && here > 0) {
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 p = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p)) continue;
                if (danger_at(s.thr, p) > enemy_here) continue;
                const double damage = cf_volley(monsters, helpers, p);
                if (damage < best) { best = damage; escape = p; }
            }
    }
    bool escaped = escape && attempt([&] { return me.move_absolute(*escape); });
    if (escaped) {
        ++s.cf_focus_exit;
        g_farm = "focus-exit";
    }
    // A trapped fighter must not just wait while monsters keep attacking.
    // With no successful escape, keep legal stationary damage on this group;
    // a fresh unsafe pull is only poked when our current tile receives no hit.
    if (!escaped && (engaged || here <= 0)) {
        bool hit = cast_offense(s, me, target, tp, false);
        if (u34_target_visible(target)) hit = basic_attack(s, me, target, tp) || hit;
        if (hit) { ++s.cf_focus_hit; s.cf_recent_camp = round; g_farm = "focus-stationary-hit"; }
    }
    // A fresh solo pull with no company is not a productive waiting objective.
    // An already damaged group retains its claim; no recall is started here.
    if (!engaged && helpers.size() == 1 && count_claimers(s, read_sm(), s.target) == 0) {
        s.groups[s.target].bad_until = round + 8;
        drop_target(s);
    }
    return false;
}

'''

EVAC = r'''
// Leave only for an ally ALREADY occupying the reward. Merely approaching or
// claiming allies never justify emptying the region and resetting capture.
bool cf_evac_reward(State& s, bc::champion& me, Group& g, int round) {
    const vec2 pos = me.position();
    if (!g.mask.is_set(pos) || !me.can_move() || !fuel_ok(28000)) return false;
    bool present = false;
    for (auto& a : bc::vision::champions(*s.my)) {
        attempt([&] {
            if (a == me || !cf_available(a) || !g.mask.is_set(a.position())) return false;
            // In particular do not rely on a recalling/teleporting ally remaining.
            present = true;
            return true;
        });
        if (present) break;
    }
    if (!present) return false;
    std::vector<std::pair<vec2, int>> monsters;
    for (const auto& c : bc::vision::camps()) {
        if (!fuel_ok(16000)) return false;
        bool observed = attempt([&] {
            // Camp wake/aggro is not exposed: avoid every visible damaging
            // monster's range, including an untouched member of an awake group.
            if (c.health() > 0 && c.strength() > 0)
                monsters.push_back({c.position(), c.attack_range()});
            return true;
        });
        if (!observed) return false; // An unknown visible hazard cannot authorize departure.
    }
    // Temporarily remove this target from scoring, without broadcasting a claim
    // or changing lifecycle memory. Failed/no-benefit moves restore all fields.
    const int old_target = s.target, old_bad = g.bad_until;
    g.bad_until = round + 1;
    int alternate = -1;
    attempt([&] { alternate = choose_target(s, me, round); return true; });
    g.bad_until = old_bad;
    if (!fuel_ok(16000)) return false;
    if (alternate < 0 || alternate == old_target) return false;
    const auto& next = s.groups[alternate];
    const int old_distance = dist(pos, next.center);
    const double current_danger = danger_at(s.thr, pos);
    std::optional<vec2> best;
    int best_distance = old_distance;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 p = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p) || g.mask.is_set(p)) continue;
            if (danger_at(s.thr, p) > current_danger) continue;
            bool monster_safe = true;
            for (const auto& c : monsters) {
                if (dist(p, c.first) <= c.second) monster_safe = false;
                if (!monster_safe) break;
            }
            if (!monster_safe) continue;
            const int d = dist(p, next.center);
            if (d < best_distance) { best = p; best_distance = d; }
        }
    if (!best || !attempt([&] { return me.move_absolute(*best); })) return false;
    ++s.cf_evac;
    s.target = alternate;
    s.target_round = round;
    s.cap_start = -1;
    write_claim(s, alternate);
    g_farm = "reward-evac";
    return true;
}

'''


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Camp transform anchor missing or ambiguous: " + old[:100])
    return text.replace(old, new, 1)


def apply_many(files, features):
    features = tuple(features)
    selected = set(features)
    if not selected <= set(FEATURES) or len(selected) != len(features):
        raise ValueError("Unknown or duplicate camp feature")
    out = dict(files)
    if not selected:
        return out
    main = out["main.cpp"]
    if "unsigned cf_reach" in main:
        raise ValueError("Camp transforms must be applied as one canonical batch")
    main = once(main, "struct State {\n    bool ready = false;\n", "struct State {\n    bool ready = false;\n" + FIELDS)
    helpers = COMMON
    if "cf_camp_focus" in selected:
        helpers += FOCUS
    if "cf_camp_evac" in selected:
        helpers += EVAC
    main = once(main, "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {",
                helpers + "void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {")
    main = once(main, "    const int round = static_cast<int>(bc::round_number());\n\n    if (!me.is_alive()) {",
                "    const int round = static_cast<int>(bc::round_number());\n    cf_observe(s, me, round);\n\n    if (!me.is_alive()) {")
    main = once(main, "        Group& g = s.groups[s.target];\n        g.next_ok = round + g.respawn",
                "        Group& g = s.groups[s.target];\n        ++s.cf_reward_gain_observed;\n        g.next_ok = round + g.respawn")
    if "cf_camp_reach" in selected:
        main = once(main, "if ((P_U34_FARM_REACH && (s.de_map == v34de::Packs)) && me.can_attack() && fuel_ok(12000))",
                    "if (P_U34_FARM_REACH && me.can_attack() && fuel_ok(12000))")
        main = once(main, "            if (local) tgt = local;", "            if (local) { if (local != tgt) ++s.cf_reach; tgt = local; }")
    if "cf_camp_focus" in selected:
        main = once(main, "        if (!engaged && needed > here) {", "        if (false && !engaged && needed > here) { // cf focus model replaces this live-camp n-squared gate")
        main = once(main, "        engage(s, me, *tgt, tgt->position(), false, true);",
                    "        if (!cf_focus_safe(s, me, live, *tgt, engaged, round)) return;\n        s.cf_recent_camp = round;\n        engage(s, me, *tgt, tgt->position(), false, true);")
    else:
        main = once(main, "        engage(s, me, *tgt, tgt->position(), false, true);",
                    "        s.cf_recent_camp = round;\n        engage(s, me, *tgt, tgt->position(), false, true);")
    if "cf_camp_evac" in selected:
        main = once(main, "        if (P_ONE_CAP && other_captures(s, me, g, s.target)) {",
                    "        if (P_ONE_CAP && other_captures(s, me, g, s.target)) {\n            if (cf_evac_reward(s, me, g, round)) return;\n            if (g.mask.is_set(pos)) return; // retain capture if no safe purposeful step exists")
    out["main.cpp"] = main
    return out


def apply(files, feature):
    return apply_many(files, [feature])
