"""Q3 recalls, Q4 help, Q5 deaths. Prints markdown."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import *
R = json.load(open(RP))
sel = load_sel(); NG = len(sel)
def pct(a, b): return '%d%%' % round(100 * a / b) if b else '-'
def med(x): x = [v for v in x if v is not None]; return st.median(x) if x else None
def q(x, p):
    x = sorted(v for v in x if v is not None)
    return x[min(len(x) - 1, int(p * len(x)))] if x else None
RC = R['recalls']
print('## Q3. Recall use\n')
print('Unit = recall attempt. Outcome: arrived (spawn jump 5 rounds later), hit_foe / hit_camp (first damage before arrival), died, moved / attacked (voluntary cancel), restart. "retry" = another start by the same champion within 6 rounds of the previous one. Reference (Mite, 101 games of 07:00 today): heal trigger hp < 50% strict, starts with the nearest foe at 7-8 tiles in 35% of cases, 9.7% interrupted, retries 59% of interruptions.\n')
print('| team | starts | per game | arrived | hit by foe | hit by camp | died | moved (cancel) | attacked (cancel) | restart | hp% med / p10 / p90 | share hp<50 | gems med / share >0 | dfoe med / p10 | dfoe <= 5 | dfoe 6-8 | dfoe >= 9 | hit by a foe in prev 3 rounds | retries | spawn dist med |')
print('|---|' * 21)
def rcrow(lab, X, ng=None):
    n = len(X)
    if not n: return
    o = collections.Counter(x['out'] for x in X)
    print('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s / %s | %s | %s / %s | %s / %s | %s | %s | %s | %s | %s | %s |' % (
        lab, n, ('%.1f' % (n / ng)) if ng else '-', pct(o['arrived'], n), pct(o['hit_foe'], n), pct(o['hit_camp'], n), pct(o['died'], n), pct(o['moved'], n), pct(o['attacked'], n), pct(o['restart'], n),
        med([x['hp'] for x in X]), q([x['hp'] for x in X], .1), q([x['hp'] for x in X], .9), pct(sum(1 for x in X if x['hp'] < 50), n),
        med([x['gems'] for x in X]), pct(sum(1 for x in X if x['gems'] > 0), n), med([x['dfoe'] for x in X]), q([x['dfoe'] for x in X], .1),
        pct(sum(1 for x in X if x['dfoe'] <= 5), n), pct(sum(1 for x in X if 6 <= x['dfoe'] <= 8), n), pct(sum(1 for x in X if x['dfoe'] >= 9), n),
        pct(sum(1 for x in X if x['hit_recent']), n), pct(sum(1 for x in X if x['retry']), n), med([x['dspawn'] for x in X])))
for who, lab in ((True, 'us'), (False, 'opp')):
    X = [x for x in RC if x['us'] == who]
    rcrow(lab + ' all', X, NG)
    for ty in sorted(set(x['ty'] for x in X)): rcrow(lab + ' ' + ty, [x for x in X if x['ty'] == ty])
print()
print('Us: recall starts by hp band / foe distance (interruption = hit_foe + hit_camp + died)\n')
print('| split | starts | arrived | interrupted | hit_foe | hit_camp | died | voluntary cancel | retries |')
print('|---|---|---|---|---|---|---|---|---|')
def rc2(lab, X):
    n = len(X)
    if not n: return
    o = collections.Counter(x['out'] for x in X)
    print('| %s | %d | %s | %s | %d | %d | %d | %d | %s |' % (lab, n, pct(o['arrived'], n), pct(o['hit_foe'] + o['hit_camp'] + o['died'], n), o['hit_foe'], o['hit_camp'], o['died'], o['moved'] + o['attacked'], pct(sum(1 for x in X if x['retry']), n)))
for who, lab in ((True, 'us'), (False, 'opp')):
    X = [x for x in RC if x['us'] == who]
    for b in ('>70', '40-70', '<40'): rc2('%s hp %s' % (lab, b), [x for x in X if x['band'] == b])
    for lo, hi, l in ((0, 3, '1-3'), (4, 4, '4'), (5, 5, '5'), (6, 6, '6'), (7, 8, '7-8'), (9, 99, '9+')): rc2('%s dfoe %s' % (lab, l), [x for x in X if lo <= x['dfoe'] <= hi])
    rc2('%s hit in prev 3 rounds' % lab, [x for x in X if x['hit_recent']])
    rc2('%s not hit recently' % lab, [x for x in X if not x['hit_recent']])
print()
print('Us: recall starts per map and per result (starts per game, arrival rate, hp med, dfoe med)\n')
print('| split | games | starts/game | arrived | hp med | dfoe med | hit_foe | hit_camp | died |')
print('|---|---|---|---|---|---|---|---|---|')
X = [x for x in RC if x['us']]
for key, vals in (('map', sorted(set(s['map'] for s in sel))), ('res', ('win', 'loss')), ('tier', ('top10', '11-20', '21-30', 'other'))):
    for v in vals:
        Y = [x for x in X if x[key] == v]; ng = sum(1 for s in sel if (s[key] if key != 'tier' else tier(s['orank'])) == v)
        if not Y: continue
        o = collections.Counter(x['out'] for x in Y)
        print('| %s %s | %d | %.1f | %s | %s | %s | %d | %d | %d |' % (key, v, ng, len(Y) / ng, pct(o['arrived'], len(Y)), med([x['hp'] for x in Y]), med([x['dfoe'] for x in Y]), o['hit_foe'], o['hit_camp'], o['died']))
print()
print('After an interruption (hit_foe / hit_camp / voluntary cancel), what the champion does in the next 10 rounds:\n')
print('| team | interrupted attempts | retry | retry within 2 rounds of the interruption | died | fought | walked | none |')
print('|---|---|---|---|---|---|---|---|')
for who, lab in ((True, 'us'), (False, 'opp')):
    X = [x for x in RC if x['us'] == who and x['after'] is not None]; n = len(X); o = collections.Counter(x['after'] for x in X)
    rg = [x for x in RC if x['us'] == who and x['retry']]
    print('| %s | %d | %s | %s | %s | %s | %s | %s |' % (lab, n, pct(o['retry'], n), pct(sum(1 for x in rg if x['retry_gap'] <= 2), n), pct(o['died'], n), pct(o['fought'], n), pct(o['walked'], n), pct(o['none'], n)))
print()
# examples
X = [x for x in RC if x['us']]
print('Examples (us): recall started with a foe within 3 and interrupted: ' + '; '.join('%s %s %s r%d hp%d%% dfoe %d gems %d -> %s' % (x['match'][:8], x['map'], x['ty'], x['r'], x['hp'], x['dfoe'], x['gems'], x['out']) for x in X if x['dfoe'] <= 3 and x['out'] in ('hit_foe', 'died'))[:700])
print()
print('Examples (us): recall interrupted by a camp: ' + '; '.join('%s %s %s r%d hp%d%%' % (x['match'][:8], x['map'], x['ty'], x['r'], x['hp']) for x in X if x['out'] == 'hit_camp')[:400])
print()
# Q4
print('## Q4. Help\n')
HL = R['helps']
print('Unit = (first hit of an episode, ally alive within 8 tiles of the victim at the previous round end). Over the next 5 rounds the ally: **fought** (attacked/cast on an enemy champion), **came** (its distance to the victim shrank by >= 2 without fighting), **kept farming** (hit a camp in >= 2 of the rounds), **moved away** (>= 2 "away" moves), **other**. Time to help = first round (0 = the hit round) at which the ally came or fought.\n')
print('| team | victim-ally pairs | fought | came | kept farming | moved away | other | time to help med | help at t0 | t1 | t2 | t3+ | victim died: help rate | victim survived: help rate |')
print('|---|' * 15)
def hlrow(lab, X):
    n = len(X)
    if not n: return
    o = collections.Counter(x['res'] for x in X); th = collections.Counter(x['t_help'] - x['r'] for x in X if x['t_help'] is not None)
    hd = [x for x in X if x['victim_died']]; hs = [x for x in X if not x['victim_died']]
    print('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (lab, n, pct(o['fought'], n), pct(o['came'], n), pct(o['kept_farming'], n), pct(o['moved_away'], n), pct(o['other'], n),
          med([x['t_help'] - x['r'] for x in X if x['t_help'] is not None]), pct(th[0], n), pct(th[1], n), pct(th[2], n), pct(sum(v for k, v in th.items() if k >= 3), n),
          pct(sum(1 for x in hd if x['res'] in ('fought', 'came')), len(hd)), pct(sum(1 for x in hs if x['res'] in ('fought', 'came')), len(hs))))
for who, lab in ((True, 'us'), (False, 'opp')):
    X = [x for x in HL if x['us'] == who]
    hlrow(lab + ' all', X)
    hlrow(lab + ' ally was farming a camp', [x for x in X if x['ally_was_farming']])
    hlrow(lab + ' ally was recalling', [x for x in X if x['ally_recalling']])
    hlrow(lab + ' ally within 3', [x for x in X if x['d0'] <= 3])
    hlrow(lab + ' ally 4-8', [x for x in X if x['d0'] > 3])
    hlrow(lab + ' ally hp < 40', [x for x in X if x['ally_hp'] < 40])
    for c in ('melee', 'caster'): hlrow(lab + ' ally ' + c, [x for x in X if x['ally_cls'] == c])
    for ty in sorted(set(x['ally_ty'] for x in X)): hlrow(lab + ' ally ' + ty, [x for x in X if x['ally_ty'] == ty])
print()
print('Us: help rate (fought or came) by map / result / tier\n')
print('| split | pairs | fought+came | kept farming |')
print('|---|---|---|---|')
X = [x for x in HL if x['us']]
for key, vals in (('map', sorted(set(s['map'] for s in sel))), ('res', ('win', 'loss')), ('tier', ('top10', '11-20', '21-30', 'other'))):
    for v in vals:
        Y = [x for x in X if x[key] == v]
        if Y: print('| %s %s | %d | %s | %s |' % (key, v, len(Y), pct(sum(1 for x in Y if x['res'] in ('fought', 'came')), len(Y)), pct(sum(1 for x in Y if x['res'] == 'kept_farming'), len(Y))))
print()
print('Examples (us): ally kept farming while the victim died: ' + '; '.join('%s %s victim %s r%d (ally %s at %d)' % (x['match'][:8], x['map'], x['ty'], x['r'], x['ally_ty'], x['d0']) for x in X if x['res'] == 'kept_farming' and x['victim_died'])[:600])
print()
# Q5
print('## Q5. Deaths\n')
D = R['deaths']
for who, lab in ((True, 'US'), (False, 'OPPONENTS')):
    X = [d for d in D if d['us'] == who]; P = [d for d in X if d['pair']]; Y = [d for d in X if not d['pair']]
    print('### %s: %d deaths (%.2f per game), %d of them pair deaths (Cassi/Issac partner died with the other), %d direct\n' % (lab, len(X), len(X) / NG, len(P), len(Y)))
    print('Direct deaths only below. Final episode = the run of enemy-champion hits (gaps <= 5) that ends in the death (camp-only deaths: from the first camp hit in the last 30 rounds). "Before" = dominant action in the 5 rounds before the first hit of the final episode; "last 5" = dominant action in the 5 rounds before death.\n')
    n = len(Y)
    print('| | count |')
    print('|---|---|')
    kk = collections.Counter(d['kkind'] for d in Y)
    print('| killing blow: champion spell / champion attack / camp | %d / %d / %d |' % (kk['spell'], kk['atk'], kk['camp']))
    print('| killer type | %s |' % ', '.join('%s %d' % kv for kv in collections.Counter(d['killer'] for d in Y).most_common(8)))
    print('| zone at death: own half / middle / enemy half | %d / %d / %d |' % (sum(1 for d in Y if d['zone'] == 'own'), sum(1 for d in Y if d['zone'] == 'middle'), sum(1 for d in Y if d['zone'] == 'enemy')))
    print('| distance to own spawn at death: med / p25 / p75; <= 6 | %s / %s / %s; %d |' % (med([d['dspawn'] for d in Y]), q([d['dspawn'] for d in Y], .25), q([d['dspawn'] for d in Y], .75), sum(1 for d in Y if d['dspawn'] <= 6)))
    print('| distance to nearest altar at death: med; <= 2 | %s; %d |' % (med([d['daltar'] for d in Y]), sum(1 for d in Y if d['daltar'] <= 2)))
    print('| doing before the final episode | %s |' % ', '.join('%s %d' % kv for kv in collections.Counter(d['before'] for d in Y).most_common()))
    print('| doing in the last 5 rounds | %s |' % ', '.join('%s %d' % kv for kv in collections.Counter(d['last5'] for d in Y).most_common()))
    print('| hp%% at the first hit of the final episode: med / p25 / p75; >= 70: ; < 40: | %s / %s / %s; %d; %d |' % (med([d['hp_first'] for d in Y]), q([d['hp_first'] for d in Y], .25), q([d['hp_first'] for d in Y], .75), sum(1 for d in Y if d['hp_first'] >= 70), sum(1 for d in Y if d['hp_first'] < 40)))
    print('| length of the final episode (rounds): med; 1 round; 2-3; 4-8; > 8 | %s; %d; %d; %d; %d |' % (med([d['ep_len'] for d in Y]), sum(1 for d in Y if d['ep_len'] == 1), sum(1 for d in Y if 2 <= d['ep_len'] <= 3), sum(1 for d in Y if 4 <= d['ep_len'] <= 8), sum(1 for d in Y if d['ep_len'] > 8)))
    print('| enemy champions dealing damage in the episode: 1 / 2 / 3+ | %d / %d / %d |' % (sum(1 for d in Y if d['nfoes'] == 1), sum(1 for d in Y if d['nfoes'] == 2), sum(1 for d in Y if d['nfoes'] >= 3)))
    print('| share of episode damage from spells: med; >= 80%%: ; camp-damage share > 50%%: | %s; %d; %d |' % (med([d['spell_share'] for d in Y]), sum(1 for d in Y if d['spell_share'] >= 80), sum(1 for d in Y if d['camp_share'] > 50)))
    print('| allies within 6 at death: 0 / 1 / 2+ ; all allies dead | %d / %d / %d ; %d |' % (sum(1 for d in Y if d['allies6'] == 0), sum(1 for d in Y if d['allies6'] == 1), sum(1 for d in Y if d['allies6'] >= 2), sum(1 for d in Y if d['allies_alive'] == 0)))
    print('| allies within 8 at the first hit: 0 / 1 / 2+ | %d / %d / %d |' % (sum(1 for d in Y if d['allies8_0'] == 0), sum(1 for d in Y if d['allies8_0'] == 1), sum(1 for d in Y if d['allies8_0'] >= 2)))
    print('| enemies within 8 at the first hit: 1 / 2 / 3+ (outnumbered: foes8 > allies8+1) | %d / %d / %d (%d) |' % (sum(1 for d in Y if d['nfoe8_0'] <= 1), sum(1 for d in Y if d['nfoe8_0'] == 2), sum(1 for d in Y if d['nfoe8_0'] >= 3), sum(1 for d in Y if d['nfoe8_0'] > d['allies8_0'] + 1)))
    print('| gems carried at death: deaths with gems / total gems lost / per game / med bag when > 0 / max | %d / %d / %.1f / %s / %d |' % (sum(1 for d in X if d['gems'] > 0), sum(d['gems'] for d in X), sum(d['gems'] for d in X) / NG, med([d['gems'] for d in X if d['gems'] > 0]), max(d['gems'] for d in X)))
    print('| recall in progress at death / recall attempted in the episode | %d / %d |' % (sum(1 for d in Y if d['recall_active']), sum(1 for d in Y if d['recall_tries'] > 0)))
    print('| retreat moves in the episode: 0 / 1-2 / 3+ ; fought back >= 1 round | %d / %d / %d ; %d |' % (sum(1 for d in Y if d['fled'] == 0), sum(1 for d in Y if 1 <= d['fled'] <= 2), sum(1 for d in Y if d['fled'] >= 3), sum(1 for d in Y if d['fought'] > 0)))
    print()
    print('Per champion type (direct deaths): \n')
    print('| type | deaths | per game drafted | hp first hit med | ep len med | fled 0 | recall tried | allies6 = 0 | spells >= 80% | gems lost | top killer |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    drafted = collections.Counter()
    for s in sel:
        for c in (s['draft'] if who else s['odraft']):
            for t in ({'cassi_issac': ['Cassi', 'Issac'], 'vesper_vale': ['VesperVale']}.get(c, [c.capitalize()])): drafted[t] += 1
    for ty in sorted(set(d['ty'] for d in Y)):
        Z = [d for d in Y if d['ty'] == ty]
        print('| %s | %d | %.2f | %s | %s | %s | %s | %s | %s | %d | %s |' % (ty, len(Z), len(Z) / drafted[ty] if drafted[ty] else 0, med([d['hp_first'] for d in Z]), med([d['ep_len'] for d in Z]), pct(sum(1 for d in Z if d['fled'] == 0), len(Z)), pct(sum(1 for d in Z if d['recall_tries'] > 0), len(Z)),
              pct(sum(1 for d in Z if d['allies6'] == 0), len(Z)), pct(sum(1 for d in Z if d['spell_share'] >= 80), len(Z)), sum(d['gems'] for d in X if d['ty'] == ty), collections.Counter(d['killer'] for d in Z).most_common(1)[0][0]))
    print()
    print('Per map / result / tier (all deaths incl. pair): deaths per game, gems lost per game\n')
    print('| split | games | deaths | per game | gems lost | per game | zone own/mid/enemy | before: farming / tributing / recalling / fighting / walking / fleeing |')
    print('|---|---|---|---|---|---|---|---|')
    for key, vals in (('map', sorted(set(s['map'] for s in sel))), ('res', ('win', 'loss')), ('tier', ('top10', '11-20', '21-30', 'other'))):
        for v in vals:
            Z = [d for d in X if d[key] == v]; ng = sum(1 for s in sel if (s[key] if key != 'tier' else tier(s['orank'])) == v)
            if not ng: continue
            b = collections.Counter(d['before'] for d in Z if not d['pair'])
            print('| %s %s | %d | %d | %.1f | %d | %.0f | %d/%d/%d | %d / %d / %d / %d / %d / %d |' % (key, v, ng, len(Z), len(Z) / ng, sum(d['gems'] for d in Z), sum(d['gems'] for d in Z) / ng,
                  sum(1 for d in Z if d['zone'] == 'own'), sum(1 for d in Z if d['zone'] == 'middle'), sum(1 for d in Z if d['zone'] == 'enemy'), b['farming'], b['tributing'], b['recalling'], b['fighting'], b['walking'], b['fleeing']))
    print()
    print('Deaths per game distribution: ' + ', '.join('%d: %d games' % kv for kv in sorted(collections.Counter(collections.Counter(d['match'] for d in X)[s['match']] for s in sel).items())))
    print()
    print('Examples: ' + '; '.join('%s %s %s r%d %s hp%d%% ep %d rounds %d foes spells %d%% allies6 %d gems %d killer %s%s' % (d['match'][:8], d['map'], d['ty'], d['r'], d['before'], d['hp_first'], d['ep_len'], d['nfoes'], d['spell_share'], d['allies6'], d['gems'], d['killer'], ' RECALLING' if d['recall_active'] else '') for d in Y[:6] + [d for d in Y if d['recall_active']][:4] + [d for d in Y if d['before'] == 'tributing'][:3])[:1800])
    print()
# cross: how we kill them
print('### How the opponents die (what we did): our damage sources in their final episodes\n')
Y = [d for d in D if not d['us'] and not d['pair']]
src = collections.Counter()
for d in Y:
    for k, v in d['dmg_src'].items(): src[k] += v
tot = sum(src.values())
print('Damage share by our champion type: ' + ', '.join('%s %s' % (k, pct(v, tot)) for k, v in src.most_common()))
print('Killing blow by our type: ' + ', '.join('%s %d' % kv for kv in collections.Counter(d['killer'] for d in Y).most_common()))
Y2 = [d for d in D if d['us'] and not d['pair']]
src = collections.Counter()
for d in Y2:
    for k, v in d['dmg_src'].items(): src[k] += v
tot = sum(src.values())
print('\nOur deaths: damage share by enemy type: ' + ', '.join('%s %s' % (k, pct(v, tot)) for k, v in src.most_common()))
