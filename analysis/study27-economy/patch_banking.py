"""Study27 combat publication: isolated, composable banking route policies.

Only main.cpp changes. Baseline helpers are pinned by exact source blocks;
other disjoint main.cpp policies may compose before or after this transform.
The risk envelope is conservative geometry, not a guarantee against fog,
future cooldowns or hidden enemies. Modes are mutually exclusive.
"""
from __future__ import annotations
import hashlib

FEATURES={
    'banking_walk':'Rank legal altar approaches by native walking distance; use walking cost for bank/chain detours, retain old lock/ownership/danger penalties.',
    'banking_risk':'Walking policy plus conservative visible-enemy approach/route exclusion and matching bounded safe-route execution; explicit legacy/unsafe fallbacks.',
}

OLD_BEST='''std::optional<vec2> best_altar(State& s, vec2 pos, int round) {
    std::optional<vec2> best;
    int bestd = 1 << 30;
    for (std::size_t i = 0; i < s.altars.size(); ++i) {
        vec2 a = s.altars[i];
        if (!s.altar_ok[i]) continue;
        if (s.vis.is_set(a)) {  // refresh what we know about enemy locks
            bool locked = attempt([&] {
                return bc::vision::has_altar_lock(a) && bc::vision::altar_lock_at(a).is_enemy();
            });
            s.lock_until[i] = locked ? round + 40 : 0;
        }
        int d = dist(a, pos);
        if (s.lock_until[i] > round) d += 40;
        if (P_ALTAR_SAFE && s.vis.is_set(a))  // an enemy champion next to the altar: prefer another one
            attempt([&] {
                for (auto& e : bc::vision::champions(*s.en))
                    if (e.is_alive() && dist(e.position(), a) <= 3) { d += P_ALTAR_SAFE; break; }
                return true;
            });
        if (P_OWN_ALTAR && static_cast<int>(i) != s.hold && dist(a, s.spawn_center) - dist(a, s.en_center) > 3) d += P_OWN_ALTAR;
        if (P_DANGER && static_cast<int>(i) != s.hold && round - s.danger_r <= P_DANGER_T && dist(a, s.danger_p) <= P_DANGER_R) d += 60;
        if (d < bestd) { bestd = d; best = a; }
    }
    return best;
}'''

OLD_GO='''bool go_tribute(State& s, bc::champion& me, int round) {
    vec2 pos = me.position();
    auto a = best_altar(s, pos, round);
    if (!a) return false;
    if (dist(pos, *a) <= 1) {
        // Against an enemy lock this is converted into an attack on the lock.
        return attempt([&] {
            me.submit_gems(*a);
            return true;
        });
    }
    bc::bitboard ring;
    ring.draw_chebyshev(*a, 1.0f);
    bool moved = step_towards(s, me, ring, true);
    if (dist(me.position(), *a) <= 1)
        attempt([&] {
            me.submit_gems(*a);
            return true;
        });
    return moved;
}'''

STATE_FIELDS='''
    // BR_BANKING_ROUTING: private per-champion, one plan per round/position.
    int br_round = -1, br_choice = -1, br_reason = 0;
    vec2 br_pos{0, 0};
    bool br_safe_route = false;
    std::vector<int> br_lengths;
    bc::bitboard br_risk_block;
    int br_decisions = 0, br_fallbacks = 0, br_routes = 0, br_stops = 0;
    int br_log_round = -1;
'''

ROUTING=r'''
// BR_BANKING_ROUTING: native walking-to-approach distance, not line distance.
constexpr int br_policy = @POLICY@;

int br_ring_distance(const bc::distance_field& field, const bc::bitboard& reached,
                     const bc::bitboard& block, vec2 altar) {
    int best = 1 << 30;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 p = altar + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || block.is_set(p) || !reached.is_set(p)) continue;
            best = std::min(best, static_cast<int>(field.get(p)));
        }
    // +1 preserves the old altar-centre distance thresholds on an open map.
    return best < (1 << 30) ? best + 1 : -1;
}

int br_altar_penalty(State& s, vec2 a, int i, int round) {
    int cost = s.lock_until[i] > round ? 40 : 0;
    if (P_ALTAR_SAFE && s.vis.is_set(a))
        attempt([&] {
            for (auto& e : bc::vision::champions(*s.en))
                if (e.is_alive() && dist(e.position(), a) <= 3) { cost += P_ALTAR_SAFE; break; }
            return true;
        });
    if (P_OWN_ALTAR && i != s.hold && dist(a, s.spawn_center) - dist(a, s.en_center) > 3) cost += P_OWN_ALTAR;
    if (P_DANGER && i != s.hold && round - s.danger_r <= P_DANGER_T && dist(a, s.danger_p) <= P_DANGER_R) cost += 60;
    return cost;
}

bool br_better(bool safe, int cost, int home, int index,
               bool old_safe, int old_cost, int old_home, int old_index) {
    if (old_index < 0) return true;
    if (br_policy == 2 && safe != old_safe) return safe;
    if (cost != old_cost) return cost < old_cost;
    if (home != old_home) return home < old_home;
    return index < old_index;
}

bool br_threat_block(State& s, vec2 pos, int round, bc::bitboard& block) {
    block = s.blocked;
    auto enemies = bc::vision::champions(*s.en);
    if (enemies.size() > 16) return false;
    for (auto& enemy : enemies) {
        if (!fuel_ok(26000)) return false;
        bool ok = attempt([&] {
            if (!enemy.is_alive()) return true;
            vec2 p = enemy.position();
            int radius = std::max(3, static_cast<int>(enemy.attack_range()) + 1);
            bool fresh = false;
            if (s.thr_r == round)
                for (const auto& threat : s.thr)
                    if (threat.p == p) {
                        radius = std::max(radius, std::max(threat.ar, std::max(threat.xr, std::max(threat.fr + 1, threat.sr + 1))));
                        fresh = true;
                        break;
                    }
            // Outside the existing fresh snapshot, reserve the generic spell
            // envelope; do not query hidden units or assume walls stop spells.
            if (!fresh) radius = std::max(radius, SPELL_RANGE + 1);
            bc::bitboard danger;
            danger.draw_chebyshev(p, static_cast<float>(radius));
            block |= danger;
            return true;
        });
        if (!ok) return false;
    }
    // A champion already in danger may escape; an adjacent altar can still be
    // used immediately. This does not mark its other threatened tiles safe.
    block.set(pos, false);
    return true;
}

bool br_plan(State& s, vec2 pos, int round) {
    if (!fuel_ok(50000) || s.altars.size() > 64) { s.br_reason = 1; return false; }
    return attempt([&] {
        bc::bitboard block = s.blocked, roots, reached;
        block.set(pos, false);
        roots.set(pos);
        bc::distance_field field;
        field.compute(block, roots, reached, 400);
        std::vector<int> ordinary(s.altars.size(), -1), safe(s.altars.size(), -1);
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
            if (s.altar_ok[i]) ordinary[i] = br_ring_distance(field, reached, block, s.altars[i]);
        }
        if (br_policy == 2) {
            if (!br_threat_block(s, pos, round, s.br_risk_block)) { s.br_reason = 2; return false; }
            bc::distance_field safe_field;
            bc::bitboard safe_reached;
            safe_field.compute(s.br_risk_block, roots, safe_reached, 400);
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
                if (ordinary[i] >= 0) safe[i] = br_ring_distance(safe_field, safe_reached, s.br_risk_block, s.altars[i]);
            }
        }
        int best = -1, best_cost = 1 << 30, best_home = 1 << 30;
        bool best_safe = false;
        s.br_lengths = ordinary;
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (ordinary[i] < 0) continue;
            const bool route_safe = br_policy == 2 && safe[i] >= 0;
            const int length = route_safe ? safe[i] : ordinary[i];
            const int cost = length + br_altar_penalty(s, s.altars[i], static_cast<int>(i), round);
            const int home = dist(s.altars[i], s.spawn_center);
            if (br_better(route_safe, cost, home, static_cast<int>(i), best_safe, best_cost, best_home, best)) {
                best = static_cast<int>(i); best_cost = cost; best_home = home; best_safe = route_safe;
            }
            if (route_safe) s.br_lengths[i] = safe[i];
        }
        if (best < 0) { s.br_reason = 3; return false; }
        s.br_choice = best;
        s.br_safe_route = best_safe;
        s.br_reason = br_policy == 2 && !best_safe ? 4 : 0;
        return true;
    });
}

std::optional<vec2> best_altar(State& s, vec2 pos, int round) {
    if (s.br_round != round || !(s.br_pos == pos)) {
        s.br_round = round; s.br_pos = pos; s.br_choice = -1;
        s.br_safe_route = false; s.br_reason = 0;
        s.br_lengths.assign(s.altars.size(), -1);
        auto fallback = br_legacy_best_altar(s, pos, round); // preserves lock refresh
        if (!br_plan(s, pos, round)) {
            if (!s.br_reason) s.br_reason = 2; // SDK failure, not a safety claim
            s.br_lengths.assign(s.altars.size(), -1);
            if (fallback)
                for (std::size_t i = 0; i < s.altars.size(); ++i)
                    if (s.altars[i] == *fallback) { s.br_choice = static_cast<int>(i); break; }
        }
    }
    if (s.br_choice < 0) return std::nullopt;
    return s.altars[s.br_choice];
}

int br_altar_distance(State& s, vec2 altar, vec2 pos, int round) {
    best_altar(s, pos, round);
    for (std::size_t i = 0; i < s.altars.size(); ++i)
        if (s.altars[i] == altar && s.br_lengths[i] >= 0) return s.br_lengths[i];
    return dist(altar, pos); // explicit legacy/fuel fallback
}

bool br_safe_move(State& s, bc::champion& me, vec2 altar) {
    vec2 pos = me.position();
    bc::bitboard goals, dest, reached;
    goals.draw_chebyshev(altar, 1.0f);
    goals &= ~s.br_risk_block;
    if (goals.is_empty()) return false;
    dest.set(pos);
    bc::distance_field field;
    bool valid = attempt([&] {
        field.compute_to(s.br_risk_block, goals, dest, reached, 400);
        return reached.is_set(pos);
    });
    if (!valid) return false; // do not silently discard the risk walls
    bool moved = false;
    if (s.dash_slot >= 0 && me.can_cast()) {
        auto ability = me.abilities()[s.dash_slot];
        const int here = field.get(pos);
        if (here >= 3 && ability.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 p = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(p) || s.br_risk_block.is_set(p) || !reached.is_set(p)) continue;
                    int distance = field.get(p);
                    if (distance < bestd) { best = p; bestd = distance; }
                }
            if (best && attempt([&] { return ability.use(*best); })) { moved = true; pos = me.position(); }
        }
    }
    if (me.can_move())
        for (auto direction : field.next_moves_from(pos))
            if (attempt([&] { return me.move(direction); })) { moved = true; break; }
    return moved;
}

void br_note(State& s, int round, int length, bool used_safe) {
    ++s.br_decisions;
    if (s.br_reason) ++s.br_fallbacks;
    if (used_safe) ++s.br_routes;
    if ((s.br_decisions <= 8 || round % 50 == 0) && s.br_log_round != round) {
        s.br_log_round = round;
        std::printf("[econ] who=%d r=%d br_decisions=%d br_fallbacks=%d br_routes=%d br_stops=%d altar=%d path=%d fallback=%d\n",
                    s.ally_idx, round, s.br_decisions, s.br_fallbacks, s.br_routes, s.br_stops, s.br_choice, length, s.br_reason);
    }
}
'''

NEW_GO=r'''bool go_tribute(State& s, bc::champion& me, int round) {
    vec2 pos = me.position();
    auto a = best_altar(s, pos, round);
    if (!a) return false;
    const int length = br_altar_distance(s, *a, pos, round);
    if (dist(pos, *a) <= 1) {
        bool acted = attempt([&] { me.submit_gems(*a); return true; });
        br_note(s, round, length, false);
        return acted;
    }
    bool moved = false, used_safe = false;
    if (br_policy == 2 && s.br_safe_route && fuel_ok(26000)) {
        used_safe = true;
        moved = br_safe_move(s, me, *a);
        if (!moved) ++s.br_stops;
    } else {
        if (br_policy == 2 && s.br_safe_route) s.br_reason = 1;
        bc::bitboard ring;
        ring.draw_chebyshev(*a, 1.0f);
        moved = step_towards(s, me, ring, true);
    }
    if (dist(me.position(), *a) <= 1)
        attempt([&] { me.submit_gems(*a); return true; });
    br_note(s, round, length, used_safe);
    return moved;
}'''


def _once(text,old,new):
    if text.count(old)!=1:raise ValueError('Banking anchor missing/duplicated: '+old[:85])
    return text.replace(old,new,1)


def apply_many(files,features):
    features=list(features)
    if len(features)!=len(set(features)) or any(f not in FEATURES for f in features):raise ValueError('Unknown/duplicate banking policy')
    if len(features)>1:raise ValueError('banking_walk and banking_risk are alternative complete policies')
    result=dict(files)
    if not features:return result
    source=result['main.cpp']
    if 'BR_BANKING_ROUTING' in source:raise ValueError('Banking policy already applied')
    source=_once(source,'    int de_map = 0;','    int de_map = 0;'+STATE_FIELDS)
    mode=1 if features[0]=='banking_walk' else 2
    source=_once(source,OLD_BEST,OLD_BEST.replace('best_altar(', 'br_legacy_best_altar(',1)+ROUTING.replace('@POLICY@',str(mode)))
    source=_once(source,OLD_GO,NEW_GO)
    for old in ('dist(*a, pos) <= std::min(home, 12)','dist(*a, pos) <= std::min(home, 8)',
                'int ad = a ? dist(*a, pos) : 99;'):
        source=_once(source,old,old.replace('dist(*a, pos)','br_altar_distance(s, *a, pos, round)'))
    result['main.cpp']=source
    return result


def apply(files,feature):return apply_many(files,[feature])
