"""Independent, checked source transforms for frozen study28 commit43d0033.

Each function mutates an LF-normalized ``dict[str, str]`` in place. No snapshot
is read or written by this module. The caller controls candidate composition.
"""


def _replace(files, old, new, name="main.cpp"):
    text = files[name]
    if "\r" in text:
        raise ValueError(f"{name} must be LF-normalized")
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one source anchor in {name}, found {count}: {old[:80]!r}")
    files[name] = text.replace(old, new, 1)


_DANGER_HELPER = '''// Bind a wire packet to the full epoch in which we observed it. Reusing an
// unchanged byte must not make its five-bit timestamp fresh after 256 rounds.
// After an ambiguous long read gap, wait for a new packet instead of guessing.
int shared_danger_round(State& s, int packet, int round) {
    const int age = ((round / 8) - (packet >> 3)) & 31;
    const int epoch = (round / 8 - age) * 8;
    const bool first = s.danger_packet_read < 0;
    const bool recent = first ? round < 256 :
        round >= s.danger_packet_read && round - s.danger_packet_read < 256;
    if (packet != s.danger_packet) {
        s.danger_packet = packet;
        s.danger_packet_epoch = recent && epoch >= 0 &&
            (first || epoch + 7 >= s.danger_packet_read) ? epoch : -1;
    }
    s.danger_packet_read = round;
    if (s.danger_packet_epoch < 0 || round < s.danger_packet_epoch ||
        (round / 8) * 8 - s.danger_packet_epoch > P_DANGER_T) return -1000;
    // Preserve the existing eight-round quantization within a known epoch.
    return s.danger_packet_epoch + round % 8;
}

'''


def danger(files):
    """Expire unchanged danger packets without changing byte7 or other writers.

    No additional SDK queries or clearing writes are introduced. A fresh byte
    identical to a long-expired one is conservatively ignored until its next
    timestamp change; direct sightings always refresh the local state.
    """
    if 'int shared_danger_round(' in files['main.cpp']:
        raise ValueError('danger transform already applied')
    _replace(files,
        '    int danger_r = -1000;   // last round an enemy pack was seen at danger_p\n',
        '    int danger_r = -1000;   // last round an enemy pack was seen at danger_p\n'
        '    int danger_packet = -1, danger_packet_epoch = -1, danger_packet_read = -1;\n')
    _replace(files,
        'void update_danger(State& s, const std::vector<Foe>& foes, int round) {\n',
        _DANGER_HELPER + 'void update_danger(State& s, const std::vector<Foe>& foes, int round) {\n')
    _replace(files,
        '        if (ai >= 0) write_sm(7, static_cast<std::uint8_t>((ai + 1) | (((round / 8) & 31) << 3)));\n',
        '''        if (ai >= 0) {
            const int packet = (ai + 1) | (((round / 8) & 31) << 3);
            s.danger_packet = packet;
            s.danger_packet_epoch = (round / 8) * 8;
            s.danger_packet_read = round;
            write_sm(7, static_cast<std::uint8_t>(packet));
        }
''')
    _replace(files,
        '''    int ai = (b & 7) - 1, age = ((round / 8) - (b >> 3)) & 31;
    if (ai < 0 || ai >= static_cast<int>(s.altars.size()) || age * 8 > P_DANGER_T) return;
    int r = round - age * 8;
''',
        '''    const int ai = (b & 7) - 1;
    const int r = shared_danger_round(s, b, round);
    if (ai < 0 || ai >= static_cast<int>(s.altars.size()) || r < 0) return;
''')


def capture_income(files):
    """Only a verified respawning group can trigger capture-income bookkeeping."""
    _replace(files,
        '''    // Capture reward arrived while standing on our target's spawn tiles.
    if (s.target >= 0 && (gems > s.last_gems || gold > s.last_gold) && s.groups[s.target].mask.is_set(pos)) {
        Group& g = s.groups[s.target];
        g.next_ok = round + g.respawn - (P_RESPAWN ? 6 : 0);
        g.reward_seen = -1;
        broadcast_cooldown(s.target, g.next_ok);
        drop_target(s);
    }
''',
        '''    // A PvP kill can also increase gold/gems on a camp tile. Confirm that
    // the target really entered its respawn cooldown before announcing capture.
    if (s.target >= 0 && (gems > s.last_gems || gold > s.last_gold) && s.groups[s.target].mask.is_set(pos)) {
        Group& g = s.groups[s.target];
        const bool captured = g.obj && attempt([&] {
            return std::holds_alternative<bc::map::camp_group_respawning>(g.obj->state());
        });
        if (captured) {
            g.next_ok = round + g.respawn - (P_RESPAWN ? 6 : 0);
            g.reward_seen = -1;
            broadcast_cooldown(s.target, g.next_ok);
            drop_target(s);
        }
    }
''')


def capture_handoff(files):
    """Do not hand a reward to an ally channeling away from its capture mask."""
    _replace(files,
        '''            if (P_CAPCLAIM ? !(claims && d <= 4) : !(d == 0 || (claims && d <= 4))) continue;
            if (P_CAPDPS) {''',
        '''            if (P_CAPCLAIM ? !(claims && d <= 4) : !(d == 0 || (claims && d <= 4))) continue;
            // On-mask recall may deliberately overlap capture. Off-mask
            // channeling allies cannot take over the waiting reward.
            if (d > 0 && (a.is_recalling() || a.is_teleporting() || a.is_submitting_gems())) continue;
            if (P_CAPDPS) {''')
