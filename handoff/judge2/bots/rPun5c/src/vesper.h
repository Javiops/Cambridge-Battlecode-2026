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
                    for (int dx = -3; dx <= 3; ++dx)
                        for (int dy = -3; dy <= 3; ++dy) {
                            vec2 t = pos + vec2(dx, dy);
                            if ((!dx && !dy) || !bc::map::is_in_bounds(t) || !ok.is_set(t) || s.blocked.is_set(t)) continue;
                            int v = sc(t);
                            if (v > bs + 500) { bs = v; bt = t; }
                        }
                    if (bt && attempt([&] { return ab.use(*bt); })) moved = 1;
                }
            }
            if (hit) {
                ++vk_hit; vk_dash += moved;
                if (fuel_ok(30000)) std::printf("[vk] r%d %d/%d thr %d\n", round, vk_hit, vk_dash, (int)thr);
                return true;
            }
        }
    }
    return false;
}

}  // namespace vesper
