#pragma once
// vesper.h - Vesper (draft slot 2, in Stellar's place: P_DRAFT_SWAP2).
// Hooks: kite_shoot_first (fight::kite, vkite-v1).
// Her emblem plan is shop part 1's generic one (champions.h legacy_plan: durab-s, jungle-s, bruiser-h, then bruiser-s
// after P_BRUISER_FILL), no health rule (hp_pick), and she switches the team to the caster mode (champ::caster_mode).

namespace vesper {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "vesper"); }

int vk_hit = 0, vk_dash = 0;  // vkite-v1 counters ([vk] log lines)

// vkite-v1 (fight::kite): with the focus in range, shoot first, then dash out of every foe's reach when the dash is
// ready; with no dash ready, still shoot unless hurt below P_VKITE_HP% and threatened. true = kite turn done.
CHAMP_HOOK bool kite_shoot_first(State& s, bc::champion& me, const std::vector<Foe*>& near, const std::vector<int>& reaches,
                                 const Foe* focus, vec2 pos, int range, int round) {
    if (P_VKITE && range > 1 && me.can_attack() && dist(pos, focus->p) <= range && is(s.name)) {  // name last: cheap tests first (fuel)
        bool thr = false;
        for (std::size_t i = 0; i < near.size(); ++i)
            if (dist(pos, near[i]->p) <= reaches[i]) thr = true;
        bool dash = s.dash_slot >= 0 && me.can_cast() && attempt([&] { return me.abilities()[s.dash_slot].is_ready(); });
        if (!thr || dash || me.health() >= P_VKITE_HP / 100.0 * me.max_health()) {
            cast_offense(s, me, focus->c, focus->p, true);
            bool hit = basic_attack(s, me, focus->c, focus->p);
            int moved = 0;
            if (hit && thr && s.dash_slot >= 0 && me.can_cast()) {
                auto ab = me.abilities()[s.dash_slot];
                bc::bitboard ok;
                if (ab.is_ready() && attempt([&] { ok = ab.valid_tiles(); return true; })) {
                    auto sc = [&](vec2 t) {
                        int th = 0;
                        for (std::size_t i = 0; i < near.size(); ++i)
                            if (dist(t, near[i]->p) <= reaches[i]) ++th;
                        int df = dist(t, focus->p);
                        return -1000 * th + (df <= SPELL_RANGE ? 300 : 0) + (df <= range ? 100 : 0) - (s.en_spawn.is_set(t) ? 5000 : 0);
                    };
                    int bs = sc(pos);
                    std::optional<vec2> bt;
                    static const int map_w = bc::map::width(), map_h = bc::map::height();  // fuelfit o19
                    for (int dx = -3; dx <= 3; ++dx)
                        for (int dy = -3; dy <= 3; ++dy) {
                            vec2 t = pos + vec2(dx, dy);
                            if (!dx && !dy) continue;
                            int th = 0;  // fuelfit o19: the best this tile can score, before any engine read
                            for (std::size_t i = 0; i < near.size(); ++i)
                                if (dist(t, near[i]->p) <= reaches[i]) ++th;
                            if (-1000 * th + 400 <= bs + 500) continue;
                            if (X(t) < 0 || Y(t) < 0 || X(t) >= map_w || Y(t) >= map_h || !ok.is_set(t) || s.blocked.is_set(t)) continue;
                            int v = sc(t);
                            if (v > bs + 500) { bs = v; bt = t; }
                        }
                    if (bt && attempt([&] { return dm_use(ab).use(*bt); })) moved = 1;
                }
            }
            if (hit) {
                ++vk_hit; vk_dash += moved;
                if (round % 100 == 0) std::printf("[vk] r%d %d/%d thr %d\n", round, vk_hit, vk_dash, (int)thr);
                return true;
            }
        }
    }
    return false;
}
// vcarry-v1 (P_VCARRY, other_captures): with a Vesper drafted she is first on shared rewards, everybody else equal.
CHAMP_HOOK int carry_rank(const std::string& n) { return is(n) ? 0 : 1; }
// lshop-v2: late fill mix from P_LSHOP_R. Vesper: t10 Power-s 4851 / Bruiser-s 3377 / Bruiser-h 964, ours all Bruiser-s.
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    (void)s; (void)o;
    return false;  // lshop-v2's Vesper Power-s fill lost (hard panel -16 with it): she keeps the plan's Bruiser-s
}

}  // namespace vesper
