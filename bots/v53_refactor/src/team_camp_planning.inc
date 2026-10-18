constexpr int SM_CLAIMS = 5;
constexpr int SM_BC_GROUP = 5, SM_BC_READY = 6;

#ifndef P_D5_PACKED_CLAIMS
#define P_D5_PACKED_CLAIMS 0
#endif

inline bool packed_claims(const State& s) {
    return P_D5_PACKED_CLAIMS && s.roster == 6 && s.groups.size() <= 63;
}
inline int claim_slots(const State& s) { return packed_claims(s) ? 6 : SM_CLAIMS; }

// Encoded claim value:0=none,1..63=group+1. No cooldown/danger byte is read.
inline std::uint8_t claim_value(const State& s, const std::array<std::uint8_t, 8>& sm, int body) {
    if (body < 0 || body >= claim_slots(s)) return 0;
    if (!packed_claims(s)) return sm[body];
    const int bit = body * 6, byte = bit / 8, shift = bit % 8;
    const unsigned word = static_cast<unsigned>(sm[byte]) | (static_cast<unsigned>(sm[byte + 1]) << 8);
    return static_cast<std::uint8_t>((word >> shift) & 63u);
}

std::array<std::uint8_t, 8> read_sm() {
    std::array<std::byte, 8> raw{};
    attempt([&] {
        bc::shared_memory.read(0, std::span<std::byte>(raw.data(), raw.size()));
        return true;
    });
    std::array<std::uint8_t, 8> out{};
    for (int i = 0; i < 8; ++i) out[i] = std::to_integer<std::uint8_t>(raw[i]);
    return out;
}

void write_sm(std::size_t off, std::uint8_t v) {
    std::byte b = static_cast<std::byte>(v);
    attempt([&] {
        bc::shared_memory.write(off, std::span<const std::byte>(&b, 1));
        return true;
    });
}

void write_claim(State& s, int group) {
    if (s.ally_idx < 0 || s.ally_idx >= claim_slots(s)) return;
    if (!packed_claims(s)) {
        write_sm(static_cast<std::size_t>(s.ally_idx), static_cast<std::uint8_t>(group + 1));
        return;
    }
    if (group < -1 || group >= static_cast<int>(s.groups.size())) return;
    // Complete this short read/modify/write before the existing fuel reserve.
    // One5-byte host write preserves the other claims and every byte5..7.
    if (!fuel_ok(2000)) return;
    std::array<std::byte, 5> raw{};
    if (!attempt([&] {
            bc::shared_memory.read(0, std::span<std::byte>(raw.data(), raw.size()));
            return true;
        })) return;
    std::uint64_t word = 0;
    for (int i = 0; i < 5; ++i)
        word |= static_cast<std::uint64_t>(std::to_integer<std::uint8_t>(raw[i])) << (i * 8);
    const int shift = s.ally_idx * 6;
    const std::uint64_t mask = std::uint64_t{63} << shift;
    word = (word & ~mask) | (static_cast<std::uint64_t>(group + 1) << shift);
    for (int i = 0; i < 5; ++i) raw[i] = static_cast<std::byte>((word >> (i * 8)) & 255u);
    attempt([&] {
        bc::shared_memory.write(0, std::span<const std::byte>(raw.data(), raw.size()));
        return true;
    });
}

int count_claimers(const State& s, const std::array<std::uint8_t, 8>& sm, int group) {
    int n = 0;
    for (int k = 0; k < claim_slots(s); ++k)
        if (k != s.ally_idx && claim_value(s, sm, k) == group + 1) ++n;
    return n;
}

// P_DPSFARM: which allies are tanks (anyone but Stellar, the casters and Ren), learned once.
inline int cap_rank(const std::string& n, bool ranged);
int tank_bits(State& s) {
    if (s.tank_bits >= 0) return s.tank_bits;
    int bits = 0;
    bool ok = attempt([&] {
        auto allies = my_roster(s);
        for (int k = 0; k < static_cast<int>(allies.size()) && k < 16; ++k) {
            std::string n = norm(bc::to_string(allies[k].champion_name()));
            bool ranged = !(starts_with(n, "issac") || starts_with(n, "vend") || starts_with(n, "varg") ||
                            starts_with(n, "ren") || starts_with(n, "marcella") || starts_with(n, "vesper"));
            if (cap_rank(n, ranged) == 3) bits |= 1 << k;
        }
        return true;
    });
    if (ok) s.tank_bits = bits;
    return bits;
}
inline bool i_am_tank(State& s) { return PR.dpsfarm && s.ally_idx >= 0 && ((tank_bits(s) >> s.ally_idx) & 1); }

void broadcast_cooldown(int group, int ready_round) {
    if (group < 0 || group > 250) return;
    write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(group + 1));
    write_sm(SM_BC_READY, static_cast<std::uint8_t>(std::clamp(ready_round / 8 + 1, 1, 250)));
}

// Learn what allies broadcast and what we can see of each group's lifecycle
// (alive / reward available / respawning with a timer).
// Camps of the live groups around us, through the group handles (cheap) instead of the
// vision scan (very expensive). Only camps whose spawn area is in view are returned, so the
// callers' health() queries do not throw.
std::vector<bc::camp> near_camps(State& s, vec2 pos) {
    // Cheap replacement for bc::vision::camps(): only groups near us, and only camps the
    // engine says are in vision (is_visible() reports hidden camps without throwing).
    std::vector<bc::camp> out;
    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks
    if (!attempt([&] { bc::vision::visible_tiles_into(tv); return true; })) return out;
    for (auto& g : s.groups) {
        if (!g.obj || dist(g.center, pos) > P_LEAN_RADIUS) continue;
        bool seen = false;  // the engine refuses group queries when no camp spawn tile is in vision
        for (auto& c : g.obj->camps())
            if (tv.is_set(c.spawn_position())) { seen = true; break; }
        if (!seen) continue;
        if (g.next_ok > 0 && g.reward_seen < 0) {  // refresh_groups saw it respawning this turn
            bool resp = false;
            attempt([&] {
                resp = std::holds_alternative<bc::map::camp_group_respawning>(g.obj->state());
                return true;
            });
            if (resp) continue;
        }
        attempt([&] {
            for (auto& c : g.obj->camps())
                if (c.is_visible()) out.push_back(c);
            return true;
        });
    }
    return out;
}

// P_CAPPRIO: capture priority by champion (lower first): Stellar, casters, Ren, tanks.
inline int cap_rank(const std::string& n, bool ranged) {
    if (starts_with(n, "stellar")) return 0;
    if (ranged) return 1;
    if (starts_with(n, "ren")) return 2;
    return 3;
}
void refresh_groups(State& s, int round) {
    auto sm = read_sm();
    int bg = static_cast<int>(sm[SM_BC_GROUP]) - 1;
    if (PR.cache && bg >= 0 && bg < static_cast<int>(s.groups.size()) && sm[SM_BC_READY] >= 251) {
        int stamp = sm[SM_BC_READY] - 251, now = (round / 16) & 3;
        Group& g = s.groups[bg];
        if ((stamp == now || stamp == ((now + 3) & 3)) && g.reward_seen < round - 1 && g.next_ok <= round &&
            cap_rank(s.name, s.ranged_me) <= 2) {
            g.reward_seen = round - 1;  // a free reward for choose_target (posted by a tank)
            g.next_ok = 0;
        }
        bg = -1;
    }
    if (bg >= 0 && bg < static_cast<int>(s.groups.size())) {
        int ready = static_cast<int>(sm[SM_BC_READY]) * 8;
        if (ready > round) s.groups[bg].next_ok = std::max(s.groups[bg].next_ok, ready);
    }
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (!g.obj) continue;
        bool visible = false;
        for (auto t : g.tiles)
            if (s.vis.is_set(t)) { visible = true; break; }
        if (!visible) continue;
        attempt([&] {
            auto st = g.obj->state();
            if (std::holds_alternative<bc::map::camp_group_respawning>(st)) {
                int timer = std::get<bc::map::camp_group_respawning>(st).timer;
                int ready = round + std::max(1, timer) + 1;
                if (P_MAPPLAN && P_MP_CHAINPLAN && g.reward_seen >= round - 3 && g.gems > 0 && dist(s.self_pos, g.center) <= 6) { s.mp_last_g = i; s.mp_last_r = round; }  // rule 9: captured next to us
                if (ready > g.next_ok + 4) broadcast_cooldown(i, ready);
                g.next_ok = std::max(g.next_ok, ready);
                g.reward_seen = -1;
            } else if (std::holds_alternative<bc::map::camp_group_reward_available>(st)) {
                g.next_ok = 0;
                g.reward_seen = round;
            } else {
                g.next_ok = 0;
                g.reward_seen = -1;
            }
            return true;
        });
    }
}

double my_dps(State& s, bc::champion& me) {
    double d = me.strength() * (s.reset_slot >= 0 ? 1.125 : 1.0);
    if (s.slots[0] == Slot::Targeted || s.slots[0] == Slot::Ground || s.slots[1] == Slot::Targeted ||
        s.slots[1] == Slot::Ground)
        d += me.focus() * 1.5 / 8.0;
    if (starts_with(s.name, "varg")) d *= 1.5;  // splash
    return std::max(d, 10.0);
}

// Smallest squad that can clear `hp_g` health of `str_g` total strength when each
// member deals `dps` and can afford to lose `afford` health: with n members the
// fight lasts hp_g/(dps*n) rounds and each takes str_g/n per round.
// P_MP_FOCUS S (mapplan, rule 4): camps with strength S+ (elks) focus one champion, so it takes the whole fight's damage:
// hp*str/(dps*n) must fit in one body, not hp*str/(dps*n*n). 0 = the old model everywhere.
#ifndef P_MP_FOCUS
#define P_MP_FOCUS 0
#endif
int squad_needed(double hp_g, double str_g, double dps, double afford) {
    if (str_g <= 0) return 1;
    const bool focus = P_MAPPLAN && P_MP_FOCUS && str_g >= P_MP_FOCUS && (!P_MP_FOCUS_FAR || g_mp_far);
    for (int n = 1; n <= 5; ++n)
        if (hp_g * str_g / (dps * n * (focus ? 1 : n)) <= afford) return n;
    return 6;
}

int allies_near(State& s, bc::champion& me, vec2 at, int radius) {
    int n = 0;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my))
            if (!(a == me) && a.is_alive() && dist(a.position(), at) <= radius) ++n;
        return true;
    });
    return n;
}

// Score every group by gems per round of champion time, counting the health it
// costs us as the recall trip needed to get that health back.
// Hit back while running: after the move, attack the weakest enemy champion still in reach.
void shoot_back(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    if (!P_SHOOT) return;
    vec2 pos = me.position();
    const Foe* best = nullptr;
    for (auto& f : foes) {
        if (f.hp <= 0 || dist(pos, f.p) > me.attack_range()) continue;
        if (!best || f.hp < best->hp) best = &f;
    }
    if (!best) return;
    if (P_SHOOT >= 2) cast_offense(s, me, best->c, best->p, true);
    basic_attack(s, me, best->c, best->p);
}

// Danger spot: an enemy pack (P_DANGER+ champions within 4 of each other) seen this turn, or
// one an ally reported in byte 7 (nearest altar index + 1, then round / 8, mod 32).
void update_danger(State& s, const std::vector<Foe>& foes, int round) {
    for (auto& f : foes) {
        if (s.en_spawn.is_set(f.p)) continue;
        int n = 0;
        for (auto& o : foes)
            if (dist(o.p, f.p) <= 4) ++n;
        if (n >= P_DANGER) {
            s.danger_p = f.p;
            s.danger_r = round;
            break;
        }
    }
    if (P_CALLHELP) return;  // byte 7 belongs to the help call then
    if (s.danger_r == round) {
        int ai = -1, ad = P_DANGER_R + 1;
        for (std::size_t i = 0; i < s.altars.size() && i < 7; ++i)
            if (dist(s.altars[i], s.danger_p) < ad) { ad = dist(s.altars[i], s.danger_p); ai = static_cast<int>(i); }
        if (ai >= 0) write_sm(7, static_cast<std::uint8_t>((ai + 1) | (((round / 8) & 31) << 3)));
        return;
    }
    int b = read_sm()[7];
    int ai = (b & 7) - 1, age = ((round / 8) - (b >> 3)) & 31;
    if (ai < 0 || ai >= static_cast<int>(s.altars.size()) || age * 8 > P_DANGER_T) return;
    int r = round - age * 8;
    if (r > s.danger_r) {
        s.danger_p = s.altars[ai];
        s.danger_r = r;
    }
}

bool grouped(const State& s, int round) { return P_GROUP && P_DANGER && s.danger_r > -1000 && round - s.danger_r <= P_GROUP; }
bool ball_on(const State& s, int round) { return (P_BALL && s.casters) || grouped(s, round); }

int choose_target_impl(State& s, bc::champion& me, int round);
// P_FUELGUARD: the dearest choose_target seen so far (it grows with the number of camp groups and with walls),
// so a caller can skip an optional re-choice when the turn could not pay for it plus a step afterwards.
int choose_target(State& s, bc::champion& me, int round) {
    if (!P_FUELGUARD) return choose_target_impl(s, me, round);
    std::uint64_t f0 = bc::fuel_remaining();
    int t = choose_target_impl(s, me, round);
    std::uint64_t f1 = bc::fuel_remaining();
    if (f0 > f1) s.ct_cost = std::max<std::uint64_t>(s.ct_cost, f0 - f1);
    return t;
}
bool can_choose(const State& s) { return !P_FUELGUARD || fuel_ok(s.ct_cost + 12000); }

int choose_target_impl(State& s, bc::champion& me, int round) {
    FP_SCOPE(15, "choose_target");
    auto sm = read_sm();
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    double dps = my_dps(s, me);
    double gold_w = (round < 600 ? P_GOLD_W_EARLY : P_GOLD_W_LATE) / 100.0;
    int best = -1;
    double best_score = 0;
    int lead_group = -1;
    std::optional<vec2> lead_p;
    if (ball_on(s, round) && s.ally_idx > 0)
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) {
                if (!allies[k].is_alive()) continue;
                if (k < claim_slots(s)) {
                    const int claim = claim_value(s, sm, k);
                    if (claim > 0) lead_group = claim - 1;
                }
                try { lead_p = allies[k].position(); } catch (...) {}
                break;
            }
            return true;
        });
    bool cached = P_FUELGUARD && P_PATHD && s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd = cached || (P_PATHD && attempt([&] {  // walking distance from here to every camp group
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    }));
    if (P_FUELGUARD && P_PATHD && have_pd && !cached) {  // the walking distance to each group, read once per tile
        s.pd_gd.assign(s.groups.size(), -1);
        attempt([&] {
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (auto t : s.groups[i].tiles)
                    if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
                s.pd_gd[i] = b < (1 << 20) ? b : -1;
            }
            s.pd_pos = pos;
            return true;
        });
    }
    auto walk = [&](const Group& g) {
        int d = dist(pos, g.center);
        if (!have_pd) return d;
        if (P_FUELGUARD && s.pd_pos == pos && s.pd_gd.size() == s.groups.size()) {
            int b = s.pd_gd[static_cast<std::size_t>(&g - s.groups.data())];
            return b >= 0 ? b : d * 3 / 2;
        }
        int b = 1 << 20;
        for (auto t : g.tiles)
            if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
        return b < (1 << 20) ? b : d * 3 / 2;
    };
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = P_HOLD && s.hold_group[i];
        if (!held && P_DANGER && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R) continue;
        int wait = g.next_ok - round;  // > 0: respawning
        int gd = walk(g);
        const bool jack_go = P_JACKGO && g.jackpot && round >= P_JACKGO;
        if (wait > 0 && !(jack_go && wait <= gd + 40) && (!P_RESPAWN || g.monolith || wait > gd + P_RESPAWN)) continue;
        if (g.gems + g.gold <= 0) continue;
        if (P_JACKPOT && g.jackpot && round < P_JACKPOT) continue;  // farm gold and buy first, as the top teams do (stampede: first visit r350-475)
        if (P_NOGOLD && g.gems <= 0 && !s.mono_only && !s.jackpot_map) continue;  // gold-only clusters give no gems (but gold is the tiebreak where only monoliths give gems)
        int claimers = count_claimers(s, sm, i);
        if (PR.dpsfarm && !i_am_tank(s))
            for (int k = 0; k < claim_slots(s); ++k)
                if (k != s.ally_idx && ((tank_bits(s) >> k) & 1) && claim_value(s, sm, k) == i + 1) --claimers;
        bool free_reward = g.reward_seen >= 0 && round - g.reward_seen < 30;
        double afford = std::max(1.0, mhp * (1.0 - P_RESERVE_PCT / 100.0));
        int needed = free_reward ? 1 : squad_needed(g.hp, g.str, dps, afford);
        bool mono_go = s.mono_only && g.monolith;  // its damage stays, so the team wears it down over several trips
        if (mono_go) needed = std::min(needed, s.roster);
        const int jack_n = std::max(1, std::min(P_JACKN, s.roster));
        if (jack_go) needed = std::min(needed, jack_n);
        if (needed > s.roster) continue;  // not with this team, not with these stats
        int cap = g.str > 0 ? std::max(needed, P_MAX_SHARE) : 1;
        if (g.str > 0 && mp_spread(s)) cap = needed;  // mapplan_game.h rule 7: no stacking past what the camp needs
        if (mono_go) cap = free_reward ? 1 : s.roster;
        if (jack_go) cap = jack_n;
        if (P_PAIR && g.str <= 0 && g.gems > 0) cap = P_PAIR;  // gem clusters: a pair kills twice as fast
        bool pot = P_POT && i < static_cast<int>(s.pot_group.size()) && s.pot_group[i];
        if (pot) cap = std::max(cap, 2);
        if (P_R34_SHARE && (s.de_map == v34de::Monolith) && !free_reward) cap = std::min(cap, std::max(needed, P_R34_SHARE));
        if (P_ONE_CAP && free_reward) cap = 1;
        if (P_PACKOPEN && round < P_PACKOPEN) cap = std::max(cap, s.roster);
        if (claimers >= cap && i != s.target && !lead) continue;
        int team = std::max(1 + claimers, needed);
        double t_clear = free_reward ? 0.0 : g.hp / (dps * team);
        double incoming = g.str * t_clear / team;
        double travel = std::max(gd, wait);
        double cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));  // recall + heal + walk back
        double rounds = travel + t_clear + 6.0 + (incoming / mhp) * cycle;
        if (P_BANKW && g.gems > 0 && g.altar_pd >= 0) rounds += P_BANKW / 100.0 * 2.0 * g.altar_pd / team;  // the bag's trip to an altar
        if (P_R34_BANKCOST && (s.de_map == v34de::Expanse || s.de_map == v34de::Monolith) && g.gems > 0 && g.altar_pd >= 0)
            rounds += ((s.de_map == v34de::Monolith ? 100 : P_R34_BANKCOST) / 100.0) * 2.0 * std::max(0, g.altar_pd - 1) / team;
        bool pack = P_PACKOPEN && round < P_PACKOPEN;  // opening: everybody on the best camp together
        double value = (g.gems + gold_w * g.gold) / (pack ? 1.0 : std::pow(static_cast<double>(team), ((g.monolith || g.hp < P_STACK_HP || mp_spread(s)) ? 100 : P_SHAREEXP) / 100.0));  // big camps (P_STACK_HP+): a joiner keeps more of the value, so champions stack there
        double score = value / std::max(1.0, rounds);
        if (needed > 1 + claimers) score *= (mp_far_trip(s, gd) && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8)
        if (claimers > 0 && g.str == 0 && !(P_PAIR && g.gems > 0 && claimers < P_PAIR) && !(pot && claimers < 2)) score *= pack ? 1.0 : 0.3;  // clusters are a solo job
        if (pot) score *= P_POT / 100.0;  // the centre pot pays 48 a pair next to the altar
        if (dist(g.center, s.en_center) < 8) score *= 0.6;    // stay off their doorstep
        if (P_HALF && !(mp_spread(s) && P_MP_HALFOFF) && dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6) score *= P_HALF / 100.0;
        if (held) score *= P_HOLD / 100.0;
        if (lead) score *= (P_BALL && s.casters) ? P_BALL : P_GROUP_W;
        else if (lead_p && dist(g.center, *lead_p) > 8) score *= 0.3;
        if (mp_chain_next(s, me, g, i, round)) score *= P_MP_CHAINPLAN / 100.0;  // rule 9: the squad moves on to the next camp
        if (i == s.target) score *= (P_MAPPLAN && P_MP_STICK && gd >= P_MP_STICK_D) ? P_MP_STICK / 100.0 : P_STICK / 100.0;  // hysteresis (mapplan_game.h rule 6)
        if (jack_go) score *= P_JACKW;
#ifdef P_DBGT
        if (round >= P_DBGT && round < P_DBGT + P_DBGT_LEN) std::printf("[dbgt] r%d %s g%d gems=%d gold=%d d=%d need=%d cl=%d wait=%d score=%.3f\n", round, s.name.c_str(), i, g.gems, g.gold, dist(pos, g.center), needed, claimers, wait, score);
#endif
        if (score > best_score) { best_score = score; best = i; }
    }
    return best;
}

std::optional<vec2> br_legacy_best_altar(State& s, vec2 pos, int round) {
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
}
// BR_BANKING_ROUTING: native walking-to-approach distance, not line distance.
