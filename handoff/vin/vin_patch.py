# vin_patch.py SRC MODE : vin-v1 (Vesper steps in). Top 10 Vesper with the nearest foe 4 tiles away (one past her range 3):
# step + attack-reset + shoot (39 of 97 ability turns) or dash + shoot (34); ours dashes away (13 of 18) and hits in 12%
# of those turns vs 22%. MODE 1: step in + reset + shoot; MODE 2: also dash in + shoot when the reset is not ready.
import sys
src, mode = sys.argv[1], int(sys.argv[2])
p = open(src + '/params.h').read()
p += '\n#ifndef P_VIN\n#define P_VIN %d  // vin-v1\n#endif\n#define P_VIN_HP 50\n' % mode
open(src + '/params.h', 'w').write(p)
v = open(src + '/vesper.h').read()
a = '    if (P_VKITE && range > 1 && me.can_attack() && dist(pos, focus->p) <= range && is(s.name)) {'
assert v.count(a) == 1
v = v.replace(a, '''    if (P_VIN && range > 1 && dist(pos, focus->p) == range + 1 && me.can_attack() && is(s.name) &&
        me.health() >= P_VIN_HP / 100.0 * me.max_health()) {
        auto thr_at = [&](vec2 t) {
            int th = 0;
            for (std::size_t i = 0; i < near.size(); ++i)
                if (dist(t, near[i]->p) <= reaches[i]) ++th;
            return th;
        };
        const int th0 = thr_at(pos);
        auto abs = me.abilities();
        const bool reset = s.reset_slot >= 0 && me.can_cast() && attempt([&] { return abs[s.reset_slot].is_ready(); });
        const bool dash = P_VIN >= 2 && s.dash_slot >= 0 && me.can_cast() && attempt([&] { return abs[s.dash_slot].is_ready(); });
        if (reset && me.can_move()) {  // step to a tile in range, no more threatened than here, then reset the attack and shoot
            std::optional<vec2> bt;
            int bth = th0 + 1;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if ((!dx && !dy) || dist(t, focus->p) > range || !bc::map::is_in_bounds(t) || s.blocked.is_set(t) || s.en_spawn.is_set(t)) continue;
                    const int th = thr_at(t);
                    if (th <= th0 && th < bth) { bth = th; bt = t; }
                }
            if (bt && attempt([&] { return me.move_absolute(*bt); })) {
                if (attempt([&] { return dm_use(abs[s.reset_slot]).use(); })) basic_attack(s, me, focus->c, focus->p);
                ++vk_in;
                return true;
            }
        } else if (dash) {  // dash to a tile in range with the fewest threats (no more than here), then shoot
            bc::bitboard ok;
            if (attempt([&] { ok = abs[s.dash_slot].valid_tiles(); return true; })) {
                std::optional<vec2> bt;
                int bth = th0 + 1;
                for (int dx = -3; dx <= 3; ++dx)
                    for (int dy = -3; dy <= 3; ++dy) {
                        vec2 t = pos + vec2(dx, dy);
                        if ((!dx && !dy) || dist(t, focus->p) > range || !bc::map::is_in_bounds(t) || !ok.is_set(t) || s.blocked.is_set(t) || s.en_spawn.is_set(t)) continue;
                        const int th = thr_at(t);
                        if (th <= th0 && th < bth) { bth = th; bt = t; }
                    }
                if (bt && attempt([&] { return dm_use(abs[s.dash_slot]).use(*bt); })) {
                    basic_attack(s, me, focus->c, focus->p);
                    ++vk_in;
                    return true;
                }
            }
        }
    }
''' + a, 1)
v = v.replace('int vk_hit = 0, vk_dash = 0;', 'int vk_hit = 0, vk_dash = 0, vk_in = 0;')
v = v.replace('std::printf("[vk] r%d %d/%d thr %d\\n", round, vk_hit, vk_dash, (int)thr);', 'std::printf("[vk] r%d %d/%d thr %d in %d\\n", round, vk_hit, vk_dash, (int)thr, vk_in);')
open(src + '/vesper.h', 'w').write(v)
