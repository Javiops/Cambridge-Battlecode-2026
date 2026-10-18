void build_shop(State& s, bc::champion& me) {
    std::size_t n = 0;
    attempt([&] {
        n = me.item_count().size();
        return true;
    });
    std::size_t i0 = P_SHOPFIX ? s.shop_next : 0;
    for (std::size_t i = i0; i < n && (P_DBGT_ALL || fuel_ok(20000)); ++i) {
        s.shop_next = i + 1;
        if (s.shop_next >= n) s.shop_done = true;
        attempt([&] {
            bc::item_type t(static_cast<std::uint32_t>(i));
            if (!t.is_purchasable()) return false;
            auto r = t.result();
            if (!r) return false;
            char stat = t.health_points() > 0 ? 'h' : (t.strength_points() > 0 ? 's' : 'f');
            if (stat == 'h') s.fallback_items.push_back(t);
            std::string fam;
            auto pas = r->passive();
            if (pas) fam = norm(bc::to_string(*pas));
            if (fam.empty() || fam == "none") {
                bool spread = r->health_points() > 0 && r->strength_points() > 0 && r->focus_points() > 0;
                fam = spread ? "bruiser" : "power";
            }
            s.shards.push_back({t, *r, stat, fam});
#ifdef P_DBGT
            if (s.ally_idx <= 0) std::printf("[item] %zu stat=%c fam=%s h=%d s=%d f=%d -> h=%d s=%d f=%d\n", i, stat, fam.c_str(), (int)t.health_points(), (int)t.strength_points(), (int)t.focus_points(), (int)r->health_points(), (int)r->strength_points(), (int)r->focus_points());
#endif
            return true;
        });
    }
    // Emblem build per champion. Families are matched by name prefix.
    if (starts_with(s.name, "ryth")) {
        s.plan = {{"jungle", 'h', 1}, {"durab", 'h', 1}, {"monster", 'h', 1}, {"power", 'h', 99}};
    } else if (starts_with(s.name, "vesper")) {
        s.plan = {{"monster", 's', 1}, {"treasure", 's', 1}, {"jungle", 'h', 1}, {"power", 's', 99}};
    } else if (s.melee) {
        s.plan = {{"jungle", 'h', 1}, {"monster", 's', 1}, {"durab", 'h', 1}, {"power", 's', 99}};
    } else {
        s.plan = {{"monster", 's', 1}, {"jungle", 'h', 1}, {"power", 's', 99}};
    }
    if (P_SHOP_PLAN) {  // what the top teams buy: the monster emblem first, then power
        if (starts_with(s.name, "cassi") && P_CASSI_HP)  // her death also kills Issac: health first
            s.plan = {{"jungle", 'h', 1}, {"durab", 'h', 1}, {"monster", 'f', 1}, {"power", 'f', 99}};
        else if (starts_with(s.name, "cassi"))
            s.plan = {{"monster", 'f', 1}, {"power", 'f', 99}};
        else if (starts_with(s.name, "ryth"))
            s.plan = {{"monster", 's', 1}, {"power", 's', 2}, {"jungle", 'h', 1}, {"power", 's', 99}};
        else
            s.plan = {{"monster", 's', 1}, {"power", 's', 3}, {"jungle", 'h', 1}, {"power", 's', 99}};
        if (P_SHOP_PLAN >= 2 && !starts_with(s.name, "cassi"))  // Mite's tank build: survive camps solo, then raw power
            s.plan = {{"durab", 's', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"power", 's', 99}};
        if (P_SHOP_PLAN == 3) {  // what the top-10 winners buy (2026-10-14 study of 169 games)
            if (starts_with(s.name, "issac"))      // their Issac: 11 power-s shards a game, ours 5.5
                s.plan = {{"power", 's', 2}, {"jungle", 's', 1}, {"power", 's', 99}};
            else if (starts_with(s.name, "tavi"))  // their Tavi buys focus; ours bought strength
                s.plan = {{"power", 'f', 1}, {"bruiser", 'f', 1}, {"power", 'f', 99}};
            else if (starts_with(s.name, "cassi")) // little gold on Cassi: power-f and one durability-h
                s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};
            else if (starts_with(s.name, "stellar"))  // top Stellar: power-f x10, durability-h
                s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};
            else if (starts_with(s.name, "ren"))      // top Ren: power-s, some power-f (retaliation is focus)
                s.plan = {{"power", 's', 1}, {"bruiser", 'h', 1}, {"power", 'f', 1}, {"power", 's', 99}};
        }
    }
    if (P_SHOPUNI && (starts_with(s.name, "ren") || starts_with(s.name, "prism") || starts_with(s.name, "stellar")))
        s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};  // the #1's casters: 8-13 power-f a game
#if defined(P_NE_POWER_OPEN) && P_NE_POWER_OPEN > 0
    // One offensive opening emblem, then the complete original melee core.
    // Preserve Jungle camp mitigation and Bruiser health for later farming.
    if (starts_with(s.name, "ryth") || starts_with(s.name, "varg") || starts_with(s.name, "vendetta"))
        s.plan = {{"power", 's', 1}, {"durab", 's', 1}, {"jungle", 's', 1},
                  {"bruiser", 'h', 1}, {"power", 's', 99}};
#endif
    // O36_REPLACE_HOOK: one quota replaces one quota; no extra150-gold step.
    opening36::replace(s.plan, s.de_map, s.name, ((s.de_map == v34de::Rows) ? P_O36_REPLACE : 0));
}

// Start-up runs in three parts (map and camp groups, fixed walking distances, roles and shop). P_FUELGUARD lets a
// part wait for the next turn when this one cannot pay for it; with enough fuel all three run in the first turn.
void init_map(State& s, bc::champion& me) {
    FP_SCOPE(27, "init-start");
#ifdef P_CONSTPROBE
    std::printf("[const] capture=%d sleep=%d respawn=%d recall=%d submit_mult=%.3f base=%d min=%d range=%d\n", static_cast<int>(bc::constants::capture_time),
                static_cast<int>(bc::constants::camp_sleep_time), static_cast<int>(bc::constants::respawn_time),
                static_cast<int>(bc::constants::recall_time), static_cast<double>(bc::constants::submit_gem_duration_multiplier),
                static_cast<int>(bc::constants::submit_gem_base_duration), static_cast<int>(bc::constants::submit_gem_minimum_duration),
                static_cast<int>(bc::constants::submit_gems_range));
#endif
    s.my = me.team();
    s.en = bc::opponent(*s.my);
    s.my_spawn = bc::map::spawn_region(*s.my);
    s.en_spawn = bc::map::spawn_region(*s.en);
    s.static_block = bc::map::walls() | bc::map::holes() | bc::map::altars() | s.en_spawn;
    s.altars = bc::map::altars().positions();
    s.lock_until.assign(s.altars.size(), 0);
    s.altar_ok.assign(s.altars.size(), 1);
    FP(29, "init-altars");
    if (P_ALTAR_REACH && P_FUELGUARD)
        attempt([&] {  // one search from where we start; an altar is usable when a tile next to it is reached
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | bc::map::altars();
            bc::bitboard roots, seen;
            roots.set(me.position());
            bc::distance_field df;
            df.compute(wall, roots, seen);
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                bc::bitboard ring;
                ring.draw_chebyshev(s.altars[i], 1.0f);
                s.altar_ok[i] = (ring & ~wall & seen).is_empty() ? 0 : 1;
            }
            return true;
        });
    else if (P_ALTAR_REACH)
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | bc::map::altars();
            vec2 home = me.position();
            bc::distance_field df;
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                bc::bitboard ring, dest, seen;
                ring.draw_chebyshev(s.altars[i], 1.0f);
                dest.set(home);
                df.compute_to(wall, ring & ~wall, dest, seen);
                s.altar_ok[i] = seen.is_set(home) ? 1 : 0;
            }
            return true;
        });
    FP(28, "init-spawn");
    s.spawn_tiles = s.my_spawn.positions();

    auto centre = [](const std::vector<vec2>& v, vec2 fallback) {
        if (v.empty()) return fallback;
        long sx = 0, sy = 0;
        for (auto p : v) { sx += X(p); sy += Y(p); }
        vec2 m(static_cast<std::int32_t>(sx / static_cast<long>(v.size())),
               static_cast<std::int32_t>(sy / static_cast<long>(v.size())));
        vec2 best = v[0];
        for (auto p : v)
            if (dist(p, m) < dist(best, m)) best = p;
        return best;
    };
    s.spawn_center = centre(s.spawn_tiles, me.position());
    attempt([&] {
        s.en_center = centre(s.en_spawn.positions(), vec2(0, 0));
        return true;
    });

    FP(21, "init-groups");
    std::vector<bc::map::camp_group> raw_groups;
    attempt([&] {
        raw_groups = bc::map::camp_groups();
        return true;
    });
    if (P_FUELGUARD) s.groups.reserve(std::min<std::size_t>(raw_groups.size(), MAX_GROUPS));
    for (auto& g : raw_groups) {
        if (s.groups.size() >= MAX_GROUPS) break;
        attempt([&] {
        Group G;
        G.mask = g.spawn_tiles();
        G.tiles = G.mask.positions();
        if (G.tiles.empty()) return false;
        G.center = centre(G.tiles, G.tiles[0]);
        G.gems = static_cast<int>(g.gem_value());
        G.gold = static_cast<int>(g.gold_value());
        G.respawn = g.max_respawn_timer();
        for (auto& c : g.camps()) {
            double h = 0, st = 0;
            monster_stats(c, h, st);
            G.hp += h;
            G.str += st;
            G.monolith = G.monolith || c.is_monolith();
            ++G.members;
        }
        G.obj = g;
        s.groups.push_back(std::move(G));
        return true;
        });
    }
    if (P_MONO) {
        bool other_gems = false, mono = false;
        for (auto& g : s.groups) {
            if (g.monolith) mono = mono || g.gems > 0;
            else other_gems = other_gems || g.gems > 0;
        }
        s.mono_only = mono && !other_gems;
    }

}

void init_paths(State& s) {
    FP_SCOPE(22, "init-dist");
    if (P_PATHD)  // walking distances that never change: our spawn and the altars to every camp group
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn;
            bc::distance_field fs, fa;
            bc::bitboard vs, va, ar;
            fs.compute(wall, s.my_spawn & ~wall, vs);
            for (std::size_t i = 0; i < s.altars.size(); ++i)
                if (s.altar_ok[i]) ar.set(s.altars[i]);
            fa.compute(wall, ar, va);
            for (auto& g : s.groups) {
                int bs = 1 << 20, ba = 1 << 20;
                for (auto t : g.tiles) {
                    if (vs.is_set(t)) bs = std::min(bs, static_cast<int>(fs.get(t)));
                    if (va.is_set(t)) ba = std::min(ba, static_cast<int>(fa.get(t)));
                }
                g.spawn_pd = bs < (1 << 20) ? bs : -1;
                g.altar_pd = ba < (1 << 20) ? ba : -1;
            }
            return true;
        });
    if (P_JACKPOT)  // a jackpot: one group with half the map's gems or more, contested (as far from both spawns)
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.my_spawn;
            bc::distance_field fe;
            bc::bitboard ve;
            fe.compute(wall, s.en_spawn & ~wall, ve);
            int total = 0;
            for (auto& g : s.groups) total += g.gems;
            for (auto& g : s.groups) {
                if (g.monolith || g.gems * 2 < total || g.spawn_pd < 0) continue;
                int be = 1 << 20;
                for (auto t : g.tiles)
                    if (ve.is_set(t)) be = std::min(be, static_cast<int>(fe.get(t)));
                g.jackpot = be < (1 << 20) && std::abs(be - g.spawn_pd) <= 6;
                if (g.jackpot) s.jackpot_map = true;
                if (g.jackpot) std::printf("[jackpot] gems=%d of %d, from us %d, from them %d\n", g.gems, total, g.spawn_pd, be);
            }
            return true;
        });
    if (P_TELE)  // walking distance to the altars from everywhere, and from our spawn
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn, ar;
            for (std::size_t i = 0; i < s.altars.size(); ++i)
                if (s.altar_ok[i]) ar.set(s.altars[i]);
            s.tele_fa.compute(wall, ar, s.tele_va);
            int b = 1 << 20;
            for (auto t : s.spawn_tiles)
                if (s.tele_va.is_set(t)) b = std::min(b, static_cast<int>(s.tele_fa.get(t)));
            s.tele_sa = b < (1 << 20) ? b : -1;
            return true;
        });
}

void init_roles(State& s, bc::champion& me) {
    FP_SCOPE(25, "init-misc");
    if (P_DRAFTUNI)  // kite/hold only with the #1's caster draft (it always has Stellar; Ren counts as melee)
        attempt([&] {
            bool st = false;
            for (auto& a : my_roster(s))
                if (starts_with(norm(bc::to_string(a.champion_name())), "stellar")) st = true;
            s.casters = st;
            if (!st && P_SWEEP >= 3) s.sweep = 2;
            if (!st && P_UNI_RN) s.rnear = 0;
            if (st && P_UNI_RENKITE && starts_with(norm(bc::to_string(me.champion_name())), "ren")) s.renkite = true;
            return true;
        });
    s.pot_group.assign(s.groups.size(), 0);
    if (P_POT)
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!s.altar_ok[i]) continue;
            int n = 0;
            for (auto& g : s.groups)
                if (g.gems > 0 && g.str <= 0 && dist(g.center, s.altars[i]) <= 4) ++n;
            if (n < 3) continue;
            s.pots.push_back(s.altars[i]);
            for (std::size_t k = 0; k < s.groups.size(); ++k)
                if (s.groups[k].gems > 0 && s.groups[k].str <= 0 && dist(s.groups[k].center, s.altars[i]) <= 4) s.pot_group[k] = 1;
        }
    if (P_CASTGATE) {
        int ranged = 0;  // the caster ball has 3+ ranged bodies; v19's melee draft has 2 (Cassi, Tavi)
        attempt([&] {
            for (auto& a : my_roster(s))
                try {
                    if (a.attack_range() > 1) ++ranged;
                } catch (...) {
                }
            return true;
        });
        s.casters = ranged >= 3;
    }
    s.hold_group.assign(s.groups.size(), 0);
    if (P_HOLD && s.casters) {
        int bd = 1 << 30;
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!s.altar_ok[i]) continue;
            int dm = dist(s.altars[i], s.spawn_center), de = dist(s.altars[i], s.en_center);
            if (std::abs(dm - de) > 4) continue;
            int n = 0;
            for (auto& g : s.groups)
                if (g.gems > 0 && dist(g.center, s.altars[i]) <= P_HOLD_R) ++n;
            if (n >= 2 && dm < bd) { bd = dm; s.hold = static_cast<int>(i); }
        }
        if (s.hold >= 0)
            for (std::size_t k = 0; k < s.groups.size(); ++k)
                s.hold_group[k] = s.groups[k].gems > 0 && dist(s.groups[k].center, s.altars[s.hold]) <= P_HOLD_R;
    }
    s.melee = me.attack_range() <= 1;
    s.ranged_me = !s.melee;
    attempt([&] {
        s.name = norm(bc::to_string(me.champion_name()));
        return true;
    });
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        attempt([&] {
            s.slots[k] = classify(abs[k]);
            return true;
        });
        if (s.slots[k] == Slot::Dash) s.dash_slot = k;
        if (s.slots[k] == Slot::Reset) s.reset_slot = k;
    }

    attempt([&] {
        auto allies = my_roster(s);
        s.roster = static_cast<int>(allies.size());
        for (std::size_t i = 0; i < allies.size(); ++i)
            if (allies[i] == me) s.ally_idx = static_cast<int>(i);
        return true;
    });

    attempt([&] {
        bc::draft_memory_buffer dm;
        if (dm.size() >= 28 && dm[0] == std::byte{'C'} && dm[1] == std::byte{'M'} &&
            dm[2] == std::byte{'B'} && dm[3] == std::byte{'1'}) {
            if (P_D34_FAMILY && dm.size() > 28) {
                int family = std::to_integer<int>(dm[28]);
                if (family >= v34de::Unknown && family <= v34de::Rows) s.de_map = family;
            }
            int tg = std::to_integer<int>(dm[24]), rc = std::to_integer<int>(dm[25]);
            int fl = std::to_integer<int>(dm[26]), lr = std::to_integer<int>(dm[27]) * 10;
            if (tg >= 5 && tg <= 200) P.tribute_gems = tg;
            if (rc >= 10 && rc <= 90) P.recall_pct = rc;
            if (fl >= 5 && fl <= 80) P.flee_pct = fl;
            if (lr >= 500 && lr <= 2000) P.late_round = lr;
        }
        return true;
    });

    FP(23, "init-shop");
    attempt([&] {
        build_shop(s, me);
        return true;
    });
    s.last_gems = static_cast<int>(me.gem_count());
    s.last_gold = static_cast<int>(me.gold_count());

    // the game plan for this map (profile.h)
    MapFeatures mf;
    mf.camps = static_cast<int>(s.groups.size());
    mf.altars = static_cast<int>(s.altars.size());
    mf.spawn_dist = dist(s.spawn_center, s.en_center);
    attempt([&] { mf.team_size = static_cast<int>(bc::draft::team_size()); return true; });
    attempt([&] { mf.area = static_cast<int>(bc::map::width() * bc::map::height()); return true; });
    apply_profile(mf);
}

#include "mapplan_game.h"

// true once start-up is complete. A part that throws is not retried (its stage is counted before it runs).
bool init(State& s, bc::champion& me) {
    if (s.init_stage == 0) { s.init_stage = 1; init_map(s, me); }
    if (s.init_stage == 1) {
        if (P_FUELGUARD && !fuel_ok(35000)) return false;
        s.init_stage = 2;
        init_paths(s);
        if (P_MAPPLAN && (P_MP_FARHOME || P_MP_FOCUS_FAR || P_MP_SPREAD || P_MP_COMPANY || P_MP_CHAINPLAN)) mp_game_plan(s);  // only the rules that need it: off = v52 games
    }
    if (s.init_stage == 2) {
        if (P_FUELGUARD && !fuel_ok(50000)) return false;
        s.init_stage = 3;
        init_roles(s, me);
        if (P_MAPPLAN && P_MP_DASHHOLE && s.dash_slot >= 0) mp_find_dashholes(s);  // mapplan_game.h rule 5
    }
    return true;
}

// ---------------------------------------------------------------------------
// Shopping
// ---------------------------------------------------------------------------
void shop(State& s, bc::champion& me) {
    for (int it = 0; it < 12 && fuel_ok(10000); ++it) {
        if (me.gold_count() < 30) return;
        auto counts = me.item_count();
        const Shard* pick = nullptr;
        for (auto& st : s.plan) {
            const Shard* sh = nullptr;
            for (auto& x : s.shards)
                if (x.stat == st.stat && starts_with(x.family, st.family)) { sh = &x; break; }
            if (!sh) continue;
            if (static_cast<int>(counts[sh->emblem]) >= st.want) continue;
            pick = sh;
            break;
        }
        bool ok = false;
        if (pick) {
            ok = attempt([&] {
                if (!me.can_buy(pick->shard, 1)) return false;
                me.buy(pick->shard, 1);
                return true;
            });
        } else {
            for (auto& t : s.fallback_items) {
                ok = attempt([&] {
                    if (!me.can_buy(t, 1)) return false;
                    me.buy(t, 1);
                    return true;
                });
                if (ok) break;
            }
        }
        if (!ok) {
#ifdef P_DBGT
            int tot = 0;
            attempt([&] { for (auto c : me.item_count()) tot += static_cast<int>(c); return true; });
            std::printf("[shopfail] %s gold=%d plan=%zu shards=%zu fb=%zu pick=%s/%c items=%d\n", s.name.c_str(), static_cast<int>(me.gold_count()), s.plan.size(), s.shards.size(), s.fallback_items.size(),
                        pick ? pick->family.c_str() : "-", pick ? pick->stat : '-', tot);
#endif
            return;
        }
    }
}

// ---------------------------------------------------------------------------
// Movement
// ---------------------------------------------------------------------------
// Step (and dash, if allowed) towards any tile of `goals_in`. Returns true if we moved.
// P_VOLLEY: modes that commit to a fight walk in on purpose; every other mode respects the volley map.
// P_VOLLEY_FIGHT 1: ranged champions respect it in fights too (melee still walk in); 2: everybody does.
#ifndef P_VOLLEY_FIGHT
#define P_VOLLEY_FIGHT 0
#endif
// P_VOLLEY_FARM 0: farming ignores it too (online v25 gave up camps on expanse/lanes with no deaths to save).
#ifndef P_VOLLEY_FARM
#define P_VOLLEY_FARM 1
#endif
