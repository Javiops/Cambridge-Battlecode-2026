#pragma once
// cassi_issac.h - Cassi & Issac, one draft pick that shares one life (legacy drafts; not in the V20 draft).
// Hooks: pair_ok (fights: commit only while the partner has half hp), twin_guard (P_TWIN, fights), twin_farm
// (P_TWINFARM, farm), and in farm the tank-follows-DPS rule sends Issac to Cassi's camp.

namespace cassi_issac {

CHAMP_HOOK bool is_cassi(const std::string& n) { return starts_with(n, "cassi"); }
CHAMP_HOOK bool is_issac(const std::string& n) { return starts_with(n, "issac"); }

// P_TEAM_FIGHT: Cassi and Issac die together, so each commits only while its partner also has half hp or more.
inline bool pair_ok(State& s, bc::champion& me) {
    if (!is_cassi(s.name) && !is_issac(s.name)) return true;
    bool ok = true;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my))
            attempt([&] {
                if (a == me || !a.is_alive()) return false;
                std::string n = norm(bc::to_string(a.champion_name()));
                if ((is_cassi(n) || is_issac(n)) && a.health() < 0.5f * a.max_health()) ok = false;
                return true;
            });
        return true;
    });
    return ok;
}

// Step 4: Cassi and Issac share one life. Returns true if this turn's move was used.
inline bool twin_guard(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    bool cassi = is_cassi(s.name), issac = is_issac(s.name);
    if (!cassi && !issac) return false;
    vec2 pos = me.position();
    std::optional<vec2> partner, nearest;
    int nd = 99;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            if (a == me || !a.is_alive()) continue;
            vec2 ap = a.position();
            if (dist(ap, pos) < nd) { nd = dist(ap, pos); nearest = ap; }
            std::string n = norm(bc::to_string(a.champion_name()));
            if ((issac && is_cassi(n)) || (cassi && is_issac(n))) partner = ap;
        }
        return true;
    });
    if (cassi) {
        int fd = 99;
        for (auto& f : foes) if (!s.en_spawn.is_set(f.p)) fd = std::min(fd, f.d);
        if (fd > 8 || nd <= 3 || !nearest) return false;
        vec2 goal = partner && dist(*partner, pos) <= nd + 4 ? *partner : *nearest;
        bool hit = fight::hit_now(s, me, foes);
        bc::bitboard ring;
        ring.draw_chebyshev(goal, 1.0f);
        bool moved = step_towards(s, me, ring, true);
        if (!hit) shoot_back(s, me, foes);
        return moved || hit;
    }
    if (!partner || dist(*partner, pos) <= 2) return false;
    int fd = 99;
    for (auto& f : foes) fd = std::min(fd, dist(f.p, *partner));
    if (fd > 8) return false;
    bool hit = fight::hit_now(s, me, foes);
    bc::bitboard ring;
    ring.draw_chebyshev(*partner, 1.0f);
    bool moved = step_towards(s, me, ring, true);
    return moved || hit;
}

// P_TWINFARM R: Issac farms Cassi's camp; with no camp claimed by Cassi he walks back to within R of her.
// Returns true when this turn's farm is done.
CHAMP_HOOK bool twin_farm(State& s, bc::champion& me, int round, vec2 pos) {
    int ck = -1;
    std::optional<vec2> cp;
    attempt([&] {
        auto allies = my_roster(s);
        for (int k = 0; k < static_cast<int>(allies.size()); ++k) {
            if (!is_cassi(norm(bc::to_string(allies[k].champion_name()))) || !allies[k].is_alive()) continue;
            ck = k;
            try { cp = allies[k].position(); } catch (...) {}
        }
        return true;
    });
    if (ck >= 0) {
        int claim = static_cast<int>(claim_value(s, read_sm(), ck)) - 1;
        if (claim >= 0 && claim < static_cast<int>(s.groups.size())) {
            if (claim != s.target) {
                s.target = claim;
                s.target_round = round;
                s.cap_start = -1;
                write_claim(s, claim);
            }
        } else if (cp && dist(*cp, pos) > PR.twinfarm && !s.my_spawn.is_set(*cp)) {
            g_farm = "twin-join";
            drop_target(s);
            bc::bitboard ring;
            ring.draw_chebyshev(*cp, 2.0f);
            step_towards(s, me, ring, false);
            return true;
        }
    }
    return false;
}

}  // namespace cassi_issac
