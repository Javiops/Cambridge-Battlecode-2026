#pragma once

// Buy only with the remainder left by ordinary shopping, then spend the lock
// on a nearby contested/enemy-side altar. No extra recall or movement is added.
bool r5_altar_lock(State& s) {
    if (!s.ready || !s.my || !fuel_ok(7000)) return false;
    return attempt([&] {
        bc::champion& me = bc::self();
        if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() ||
            me.is_teleporting() ||
            me.restrictions().contains(bc::buff_restrictions::consumable)) return false;
        const vec2 here = me.position();
        const auto kind = bc::consumable_type::altar_lock;
        const auto& lock = me.consumables()[kind];
        auto owned = lock.count();
        if (!owned && s.my_spawn.is_set(here)) {
            const auto gold = me.gold_count();
            if (gold >= kind.cost() && gold < 30 && me.can_buy(kind)) {
                me.buy(kind);
                owned = lock.count();
            }
        }
        if (!owned) return false;
        int best = -1, rank = 1 << 20;
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            const vec2 a = s.altars[i];
            if (dist(here, a) > 2 || dist(a, s.en_center) > dist(a, s.spawn_center) + 4) continue;
            if (bc::vision::has_altar_lock(a) && bc::vision::altar_lock_at(a).is_ally()) continue;
            const int score = dist(a, s.en_center);
            if (score < rank) { rank = score; best = static_cast<int>(i); }
        }
        return best >= 0 && fuel_ok(4000) && dm_use(lock).use(s.altars[best]);
    });
}
