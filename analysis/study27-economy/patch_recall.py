"""Capture recalls as a travel-cost decision; emergency recall stays unchanged."""
FEATURES = {
    'cr_tavi': 'Exclude Tavi from gold-only opportunistic capture recalls.',
    'cr_travel': 'Tavi fix plus walking-cost-aware optional healing/shopping recalls.',
    'share85': 'Camp stacking value exponent 0.85, without changing reward splitting.',
    'share100': 'Camp stacking value exponent 1.00, without changing reward splitting.',
}

FIELDS = '''    // Capture-recall optional economy policy. Static return-trip distances.
    bc::distance_field cr_home_df;
    bc::bitboard cr_home_seen;
    bool cr_home_ready = false;
    int cr_home_retry = -1;
    int cr_seen = 0, cr_skipped = 0, cr_tavi_skipped = 0;
    int cr_path_unavailable = 0, cr_started = 0, cr_log_round = -1;
'''

PREDICATE = '''// Heuristic benefit threshold for an OPTIONAL trip, not an emergency-heal veto.
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
'''

HELPERS = '''
void cr_trace(State& s, int round) {
    if (s.cr_log_round == round) return;
    if (s.cr_seen + s.cr_started > 8 && round % 50 != 0) return;
    s.cr_log_round = round;
    std::printf("[econ] who=%d r=%d cr_opportunity=%d cr_skipped=%d cr_tavi_skipped=%d cr_path_unavailable=%d cr_started=%d\\n",
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
    const int walk = CR_TRAVEL_POLICY ? cr_return_walk(s, me.position(), round) : 0;
    const bool result = cr_optional_value(hpr, gold, tavi, shop_ok, walk, CR_TRAVEL_POLICY);
    if (old_optional && eligible_reward) {
        ++s.cr_seen;
        if (!result) ++s.cr_skipped;
        if (tavi && hpr >= 0.9f && gold >= 90 && !result) ++s.cr_tavi_skipped;
        if (CR_TRAVEL_POLICY && walk < 0) ++s.cr_path_unavailable;
        cr_trace(s, round);
    }
    return result;
}

'''

OLD_CAP = '''    bool cap_want = want_recall || (((s.de_map == v34de::Lanes) ? 1 : P_CAPRECALL) >= 2 && (hpr < 0.9f || gold >= 90));'''
NEW_CAP = '''    // Preserve normal healing/shop recalls. Only the extra capture opportunity
    // weighs the cost of returning to productive territory.
    bool cap_want = want_recall || (((s.de_map == v34de::Lanes) ? 1 : P_CAPRECALL) >= 2 &&
                                   cr_capture_extra(s, me, hpr, gold, round));'''

OLD_START = '''                if (attempt([&] {
                        me.recall();
                        return true;
                    }) && shop_trip)
                    s.shop_recall = round;
                return;'''
NEW_START = '''                if (attempt([&] {
                        me.recall();
                        return true;
                    })) {
                    ++s.cr_started;
                    cr_trace(s, round);
                    if (shop_trip) s.shop_recall = round;
                }
                return;'''

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError('Recall transform anchor mismatch: '+old[:90])
    return text.replace(old, new, 1)

def apply_many(files, features):
    features = tuple(features)
    if not features or any(f not in FEATURES for f in features):
        raise ValueError('Unknown/empty recall features')
    if len(features) != len(set(features)):
        raise ValueError('Duplicate recall features')
    result = dict(files)
    share = [f for f in features if f in ('share85', 'share100')]
    if len(share) > 1:
        raise ValueError('Stacking exponents are mutually exclusive')
    if share:
        value = 85 if share[0] == 'share85' else 100
        old = '#define P_SHAREEXP 75        // study27: a champion joining a big camp values it at gems / team^0.75 (was an even split)'
        new = f'#define P_SHAREEXP {value}  // heuristic camp participation cost; actual capture rewards still split evenly'
        result['params.h'] = replace_once(result['params.h'], old, new)
    if not any(f in features for f in ('cr_tavi', 'cr_travel')):
        return result
    text = result['main.cpp']
    travel = 'true' if 'cr_travel' in features else 'false'
    fields = FIELDS
    helpers = (PREDICATE+HELPERS).replace('CR_TRAVEL_POLICY', travel)
    if travel == 'false':
        for line in ('    bc::distance_field cr_home_df;\n', '    bc::bitboard cr_home_seen;\n',
                     '    bool cr_home_ready = false;\n', '    int cr_home_retry = -1;\n'):
            fields = fields.replace(line, '')
        start = helpers.index('int cr_return_walk(')
        end = helpers.index('bool cr_capture_extra(', start)
        helpers = helpers[:start]+helpers[end:]
        helpers = helpers.replace('false ? cr_return_walk(s, me.position(), round) : 0', '0')
    text = replace_once(text, '    int de_map = 0;\n', fields+'    int de_map = 0;\n')
    text = replace_once(text, 'void play_turn(State& s) {', helpers+'void play_turn(State& s) {')
    text = replace_once(text, OLD_CAP, NEW_CAP)
    text = replace_once(text, OLD_START, NEW_START)
    result['main.cpp'] = text
    return result

def apply(files, feature):
    return apply_many(files, [feature])
