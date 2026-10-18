void log_init(State& s) {
    std::printf("[init] %s melee=%d ally=%d groups=%zu altars=%zu spawn=%zu shards=%zu slots=%s/%s pots=%zu sm=%zu\n",
                s.name.c_str(), s.melee ? 1 : 0, s.ally_idx, s.groups.size(), s.altars.size(),
                s.spawn_tiles.size(), s.shards.size(), slot_name(s.slots[0]), slot_name(s.slots[1]), s.pots.size(),
                bc::shared_memory.size());
#ifdef P_RANGES
    attempt([&] {
        bc::champion& me = bc::self();
        auto abs = me.abilities();
        for (int k = 0; k < 2; ++k) {
            auto inf = abs[k].info();
            if (!inf) continue;
            std::visit([&](auto& x) {
                using T = std::decay_t<decltype(x)>;
                float r = -1, rad = -1, mod = -1; int dur = -1;
                if constexpr (requires { x.range; }) r = x.range;
                if constexpr (requires { x.radius; }) rad = x.radius;
                if constexpr (requires { x.modifier; }) mod = x.modifier;
                if constexpr (requires { x.duration; }) dur = x.duration;
                std::printf("[range] %s slot%d %s range=%.1f radius=%.1f mod=%.2f dur=%d cd=%d atk_range=%.1f\n", s.name.c_str(), k,
                            slot_name(s.slots[k]), r, rad, mod, dur, x.max_cooldown, static_cast<float>(me.attack_range()));
                (void)sizeof(T);
            }, *inf);
        }
        return true;
    });
#endif
    if (s.hold >= 0 && s.ally_idx <= 0) {
        int n = 0;
        for (char h : s.hold_group) n += h;
        std::printf("[hold] altar %d,%d groups %d\n", X(s.altars[s.hold]), Y(s.altars[s.hold]), n);
    }
#ifdef P_MAPDUMP
    if (s.ally_idx <= 0) {
        static char grid[64][65];
        for (auto& r : grid) { std::memset(r, '.', 64); r[64] = 0; }
        int W = 0, H = 0;
        auto put = [&](const std::vector<vec2>& v, char c) {
            for (auto t : v) if (X(t) >= 0 && X(t) < 64 && Y(t) >= 0 && Y(t) < 64) { grid[Y(t)][X(t)] = c; W = std::max(W, X(t) + 1); H = std::max(H, Y(t) + 1); }
        };
        put(bc::map::walls().positions(), '#');
        put(bc::map::holes().positions(), 'o');
        put(bc::map::altars().positions(), 'A');
        put(s.my_spawn.positions(), 'S');
        put(s.en_spawn.positions(), 'E');
        for (std::size_t i = 0; i < s.groups.size(); ++i) put(s.groups[i].tiles, static_cast<char>(i < 26 ? 'a' + i : 'A' + i - 26));
        for (int y = 0; y < H; ++y) { grid[y][W] = 0; std::printf("[map] %s\n", grid[y]); }
    }
#endif
#ifdef P_DBGT
    if (s.ally_idx <= 0) {
        namespace K = bc::constants;
        std::printf("[const] capture=%d sleep=%d respawn=%d recall=%d submit_mult=%.3f submit_base=%d submit_min=%d submit_range=%d passive_gold=%u\n",
                    (int)K::capture_time, (int)K::camp_sleep_time, (int)K::respawn_time, (int)K::recall_time,
                    K::submit_gem_duration_multiplier, (int)K::submit_gem_base_duration, (int)K::submit_gem_minimum_duration,
                    (int)K::submit_gems_range, (unsigned)K::passive_gold);
        for (std::size_t i = 0; i < s.groups.size(); ++i) {
            auto& g = s.groups[i];
            std::printf("[group] g%zu at (%d,%d) gems=%d gold=%d hp=%.0f str=%.0f members=%d mono=%d respawn=%d dmine=%d den=%d\n", i,
                        X(g.center), Y(g.center), g.gems, g.gold, g.hp, g.str, g.members, g.monolith ? 1 : 0, (int)g.respawn,
                        dist(g.center, s.spawn_center), dist(g.center, s.en_center));
        }
    }
#endif
    std::fflush(stdout);
}

void log_status(State& s) {
    attempt([&] {
        int round = static_cast<int>(bc::round_number());
#ifdef P_DBGT
        bool every = round >= P_DBGT && round < P_DBGT + P_DBGT_LEN;
#else
        bool every = false;
#endif
        if (P_TRACE) {
            bc::champion& me = bc::self();
            vec2 p = me.is_alive() ? me.position() : vec2(-1, -1);
            int rw = 0;  // groups with a waiting reward within 3 tiles of us
            if (me.is_alive())
                for (auto& g : s.groups)
                    if (g.reward_seen == round) { int d = 99; for (auto t : g.tiles) d = std::min(d, dist(p, t)); if (d <= 3) ++rw; }
            std::printf("T %d %d %d %d %d %.0f %u %u %s %s %d %d %d %d %d %d %d\n", round, s.ally_idx, X(p), Y(p),
                        me.is_alive() ? 1 : 0, me.is_alive() ? 100.0 * me.health() / me.max_health() : 0.0,
                        me.gem_count(), me.gold_count(), g_mode, g_farm, s.target, g_rew, rw, g_nf, g_nfoes, g_nal,
                        (me.is_recalling() ? 1 : 0) | (me.is_submitting_gems() ? 2 : 0));
            std::fflush(stdout);
            g_nf = 99; g_nfoes = 0; g_nal = 0; g_rew = 0;
            return true;
        }
        if (round % STATUS_EVERY != 0 && round > 3 && !every) return false;
        if (P_FUELGUARD && !fuel_ok(12000)) return false;  // a log line is not worth a turn cut short
        bc::champion& me = bc::self();
        vec2 p = me.position();
        std::printf("[r%d] %s pos=(%d,%d) hp=%.0f/%.0f gems=%u gold=%u mode=%s farm=%s target=%d errs=%d fuel=%llu\n",
                    round, s.name.c_str(), X(p), Y(p), me.health(), me.max_health(), me.gem_count(),
                    me.gold_count(), g_mode, g_farm, s.target, g_errors,
                    static_cast<unsigned long long>(bc::fuel_remaining()));
        std::fflush(stdout);
        return true;
    });
}

// P_SWEEP: stun the closest foe that can reach us next round, else damage the weakest foe in range, else stun it.
