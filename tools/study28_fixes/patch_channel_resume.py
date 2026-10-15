"""Alternative channel fix: resume ordinary decisions without same-turn restart.

This patch is mutually exclusive with patch_combat.channel. It composes with
patch_combat.dash and the independent non-channel fixes.
"""
from __future__ import annotations

import re


def _replace(files: dict[str, str], before: str, after: str, count: int = 1) -> None:
    source = files['main.cpp']
    assert '\r' not in source, 'main.cpp: expected LF source'
    assert source.count(before) == count, f'main.cpp: expected {count} replacement anchors'
    files['main.cpp'] = source.replace(before, after)


def channel_resume(files: dict[str, str]) -> None:
    """Prevent restarts only on a successful cancellation's current round."""
    _replace(files, '''struct State {
    bool ready = false;
''', '''struct State {
    bool ready = false;
    int cancelled_channel_round = -1000;
    vec2 cancelled_channel_pos{0, 0};
''')
    _replace(files, '''        g_mode = "cancelled";  // P_CHANCANCEL: the turn goes on (flee, fight, bank elsewhere)
''', '''        s.cancelled_channel_round = round;
        s.cancelled_channel_pos = pos;
        g_mode = "cancelled";  // Resume the ordinary fight/farm decisions.
''')
    _replace(files, '''    if (!fuel_ok(15000)) {
        g_mode = "low-fuel";
''', '''    const bool cancelled_channel = s.cancelled_channel_round == round;
    if (!fuel_ok(15000)) {
        g_mode = "low-fuel";
''')
    _replace(files, '''    bool rsafe = safe || (s.rnear && nearest_foe >= s.rnear && round - s.hit_round >= 1 && !awake_camp_near);
''', '''    bool rsafe = safe || (s.rnear && nearest_foe >= s.rnear && round - s.hit_round >= 1 && !awake_camp_near);
    if (cancelled_channel) {
        // Do not immediately restart an interrupted recall, including capture/tele recalls.
        safe = false;
        rsafe = false;
    }
''')
    _replace(files, '''        vec2 a = s.altars[i];
        if (!s.altar_ok[i]) continue;
''', '''        vec2 a = s.altars[i];
        if (!s.altar_ok[i]) continue;
        // Try another altar rather than starting a channel at the cancelled position.
        if (s.cancelled_channel_round == round && dist(a, s.cancelled_channel_pos) <= 1) continue;
''')
    _replace(files, '''bool go_tribute(State& s, bc::champion& me, int round) {
    vec2 pos = me.position();
''', '''bool go_tribute(State& s, bc::champion& me, int round) {
    vec2 pos = me.position();
    const bool cancelled_channel = s.cancelled_channel_round == round;
''')
    _replace(files, '''    if (dist(pos, *a) <= 1) {
        // Against an enemy lock this is converted into an attack on the lock.
''', '''    if (dist(pos, *a) <= 1) {
        if (cancelled_channel && pos == s.cancelled_channel_pos) return false;
        // Against an enemy lock this is converted into an attack on the lock.
''')
    _replace(files, '''    if (dist(me.position(), *a) <= 1)
        attempt([&] {
            me.submit_gems(*a);
''', '''    if (dist(me.position(), *a) <= 1 &&
        (!cancelled_channel || !(me.position() == s.cancelled_channel_pos)))
        attempt([&] {
            me.submit_gems(*a);
''')
    _replace(files, 'if (acted || !P_U34_FAILED_CHANNELS) return;',
             'if (acted || (!P_U34_FAILED_CHANNELS && !cancelled_channel)) return;', count=4)
    _replace(files, 'if (recalled || !P_U34_FAILED_CHANNELS) return;',
             'if (recalled || (!P_U34_FAILED_CHANNELS && !cancelled_channel)) return;')
    _replace(files, 'if (!rsafe || (P_U34_FAILED_CHANNELS && !recalled)) {',
             'if (!rsafe || ((P_U34_FAILED_CHANNELS || cancelled_channel) && !recalled)) {')

    # All six recall action sites are in play_turn and share this local guard.
    # safe/rsafe also skip their unconditional-return callers on a cancelled turn.
    source = files['main.cpp']
    pattern = r'(?m)^( +)me\.recall\(\);$'
    assert len(re.findall(pattern, source)) == 6, 'Expected exactly six recall action sites'
    source = re.sub(pattern, lambda m: m[1]+'if (cancelled_channel) return false;\n'+m[0], source)
    files['main.cpp'] = source
