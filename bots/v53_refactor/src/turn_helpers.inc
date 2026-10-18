bool cm_edge_aoe(State& s, bc::champion& me, bool allow_exclusive, bool track_root,
                 bool free_only = false, bool escape = false) {
    if (s.sweep < 3 || !me.can_cast() || !fuel_ok(16000)) return false;
    const vec2 pos = me.position();
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        if (s.slots[k] != Slot::Ground || !abs[k].is_ready()) continue;
        const AoeSlot a = aoe_slot(me, k);
        if (a.radius <= 0) continue;
        const bool exclusive = slot_exclusive(s, me, k);
        if (exclusive && (!allow_exclusive || free_only || escape)) continue;
        std::optional<vec2> best;
        double best_score = -1e30;
        for (auto& c : bc::vision::champions(*s.en)) {
            if (!fuel_ok(8000)) return false;
            attempt([&] {
                if (!c.is_visible() || !c.is_alive() || c.health() <= 0) return false;
                const vec2 p = c.position();
                const int d = dist(pos, p);
                if (s.en_spawn.is_set(p) || d <= SPELL_RANGE || d > a.range + a.radius) return false;
                int hits = 0;
                vec2 centre = aoe_centre(s, me, k, p, &hits);
                if (hits <= 0 || dist(pos, centre) > a.range || dist(centre, p) > a.radius) return false;
                const double score = hits * 1000.0 - c.health();
                if (score > best_score) { best = centre; best_score = score; }
                return true;
            });
        }
        if (best && attempt([&] { return abs[k].use(*best); })) {
            if (track_root && exclusive) s.rooted_r = static_cast<int>(bc::round_number());
            return true;
        }
    }
    return false;
}

// Heuristic benefit threshold for an OPTIONAL trip, not an emergency-heal veto.
// Longer return walks require a larger heal or a larger gold budget. Tavi shops
// in the field, so gold alone never justifies this optional return.
bool cr_optional_value(float hpr, int gold, bool tavi, bool shop_ok,
                       int return_walk, bool travel_policy) {
    if (!travel_policy) return hpr < 0.9f || (!tavi && gold >= 90);
    if (return_walk < 0) return false;
    const float heal_cutoff = std::clamp(0.9f - 0.006f * return_walk, 0.65f, 0.9f);
    const int gold_cutoff = 90 + 3 * std::min(return_walk, 50);
    return hpr < heal_cutoff || (!tavi && shop_ok && gold >= gold_cutoff);
}

void cr_trace(State& s, int round) {
    if (s.cr_log_round == round) return;
    if (s.cr_seen + s.cr_started > 8 && round % 50 != 0) return;
    s.cr_log_round = round;
    std::printf("[econ] who=%d r=%d cr_opportunity=%d cr_skipped=%d cr_tavi_skipped=%d cr_path_unavailable=%d cr_started=%d\n",
                s.ally_idx, round, s.cr_seen, s.cr_skipped, s.cr_tavi_skipped,
                s.cr_path_unavailable, s.cr_started);
}

int cr_return_walk(State& s, vec2 pos, int round) {
    if (!s.cr_home_ready && round >= s.cr_home_retry) {
        s.cr_home_retry = round + 16;
        if (fuel_ok(22000)) {
            s.cr_home_ready = attempt([&] {
                bc::bitboard roots = s.my_spawn & ~s.static_block;
                s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
                return true;
            });
        }
    }
    if (!s.cr_home_ready || !s.cr_home_seen.is_set(pos)) return -1;
    return static_cast<int>(s.cr_home_df.get(pos));
}

bool cr_capture_extra(State& s, bc::champion& me, float hpr, int gold, int round) {
    const bool tavi = starts_with(s.name, "tavi");
    const bool old_optional = hpr < 0.9f || gold >= 90;
    const bool eligible_reward = s.target >= 0 && s.target < static_cast<int>(s.groups.size()) &&
        s.groups[s.target].reward_seen == round && s.groups[s.target].mask.is_set(me.position());
    const bool shop_ok = (!P_SHOPFIX || round - s.shop_fail > 150) && round - s.shop_recall > 40;
    const int walk = true ? cr_return_walk(s, me.position(), round) : 0;
    const bool result = cr_optional_value(hpr, gold, tavi, shop_ok, walk, true);
    if (old_optional && eligible_reward) {
        ++s.cr_seen;
        if (!result) ++s.cr_skipped;
        if (tavi && hpr >= 0.9f && gold >= 90 && !result) ++s.cr_tavi_skipped;
        if (true && walk < 0) ++s.cr_path_unavailable;
        cr_trace(s, round);
    }
    return result;
}

