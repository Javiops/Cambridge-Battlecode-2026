"""Independent, composable patches against immutable study28 LF source strings."""
from __future__ import annotations


def _replace(files: dict[str, str], name: str, before: str, after: str) -> None:
    source = files[name]
    assert '\r' not in source, f'{name}: expected LF source'
    assert source.count(before) == 1, f'{name}: expected one replacement anchor'
    files[name] = source.replace(before, after, 1)


def channel(files: dict[str, str]) -> None:
    """After a successful channel cancel, escape instead of starting it again."""
    _replace(files, 'main.cpp', '''    if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) {
        g_mode = "channel";
        if (!(P_CHANCANCEL && !me.is_teleporting() && !on_spawn && cancel_doomed_channel(s, me, hp))) return;
        g_mode = "cancelled";  // P_CHANCANCEL: the turn goes on (flee, fight, bank elsewhere)
    }
''', '''    bool cancelled_channel = false;
    if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) {
        g_mode = "channel";
        if (!(P_CHANCANCEL && !me.is_teleporting() && !on_spawn && cancel_doomed_channel(s, me, hp))) return;
        cancelled_channel = true;
    }
''')
    _replace(files, 'main.cpp', '''    support_spells(s, me, in_combat);
''', '''    if (cancelled_channel) {
        // Use fresh occupancy and threats, and never restart a channel this turn.
        // A normal, uninterrupted capture/recall overlap keeps its original path.
        g_mode = "channel-escape";
        if (!fight::safe_step(s, me, foes)) flee(s, me);
        shoot_back(s, me, foes);
        return;
    }

    support_spells(s, me, in_combat);
''')


def dash(files: dict[str, str]) -> None:
    """Share the ready dash + ordinary move + melee attack envelope."""
    _replace(files, 'main.cpp', '''    bool excl = false;
};
struct ChampSpells {
''', '''    bool excl = false;
    int dash_range = -1;  // -1: metadata unavailable; 0: not a dash
};
struct ChampSpells {
''')
    _replace(files, 'main.cpp', '''                    SpellInfo& si = cs.k[k];
                    if constexpr (T::kind == bc::ability_kind::attack_reset) {
                        si.kind = 1;
                    } else if constexpr (T::kind == bc::ability_kind::damage || T::kind == bc::ability_kind::aoe_damage ||
''', '''                    SpellInfo& si = cs.k[k];
                    si.dash_range = 0;
                    if constexpr (T::kind == bc::ability_kind::attack_reset) {
                        si.kind = 1;
                    } else if constexpr (T::kind == bc::ability_kind::dash) {
                        si.dash_range = std::max(0, static_cast<int>(x.range));
                    } else if constexpr (T::kind == bc::ability_kind::damage || T::kind == bc::ability_kind::aoe_damage ||
''')
    _replace(files, 'main.cpp', '''inline Threat threat_of(bc::champion c, vec2 p, int atk_reach) {
''', '''inline int next_attack_reach(const bc::champion& c) {
    int range = 1;
    attempt([&] {
        range = static_cast<int>(c.attack_range());
        return true;
    });
    if (range > 1) return range + 1;  // Preserve the existing ranged envelope.

    // Metadata is cached per champion type. Cooldowns are read outside tile loops.
    // A failed query keeps the documented two-tile dash as a conservative bound.
    const ChampSpells& cs = spells_of(c);
    int dash_range = 0;
    for (int k = 0; k < 2; ++k)
        dash_range = std::max(dash_range, cs.k[k].dash_range < 0 ? 2 : cs.k[k].dash_range);
    if (dash_range > 0)
        attempt([&] {
            auto abs = c.abilities();
            int ready_dash = 0;
            for (int k = 0; k < 2; ++k) {
                const int r = cs.k[k].dash_range;
                if (r < 0) ready_dash = std::max(ready_dash, 2);
                else if (r > 0 && abs[k].cooldown() == 0) ready_dash = std::max(ready_dash, r);
            }
            dash_range = ready_dash;
            return true;
        });
    return range + 1 + dash_range;  // Melee attack + ordinary move + ready dash.
}

inline Threat threat_of(bc::champion c, vec2 p, int atk_reach) {
''')
    _replace(files, 'main.cpp', '''            int ar = 1;
            attempt([&] {
                ar = static_cast<int>(f.c.attack_range());
                return true;
            });
            s.thr.push_back(threat_of(f.c, f.p, ar <= 1 ? 2 : ar + 1));
''', '''            s.thr.push_back(threat_of(f.c, f.p, next_attack_reach(f.c)));
''')
    _replace(files, 'fight.h', '''// How far a foe can hit next round: melee 2 (3 with a dash), ranged its range + 1.
inline int reach(const Foe& f) {
    int r = 1;
    attempt([&] {
        r = static_cast<int>(f.c.attack_range());
        return true;
    });
    if (r <= 1) {
        std::string n;
        attempt([&] {
            n = norm(bc::to_string(f.c.champion_name()));
            return true;
        });
        // Melee champions with a dash: Vendetta, Issac and Ren (Cassi is ranged and has none; the old list said
        // "cassi", so Issac's dash was missed). P_DASHFIX 0 keeps the old list for measuring.
        bool dash = starts_with(n, "vend") || starts_with(n, P_DASHFIX ? "issac" : "cassi") || starts_with(n, "ren");
        return dash ? 3 : 2;
    }
    return r + 1;
}
''', '''// Next-turn attack envelope, including a ready dash and an ordinary move.
inline int reach(const Foe& f) {
    return next_attack_reach(f.c);
}
''')
