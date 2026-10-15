import json, collections, statistics as st
D = json.load(open('summaries.json'))
SEL = json.load(open('/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws/selected.json'))
RES = {(r['match'], r['team']): r['res'] for r in SEL}
for d in D: d['res'] = RES[(d['match'], d['team'])]
maps = ['rows','expanse','lanes','monolith','packs','collision','corners','elkring','interlock']
def rng(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return '-'
    return str(xs[0]) if min(xs) == max(xs) else '%d-%d' % (min(xs), max(xs))
print('## A. first camp per map/team (6 games each)')
print('| map | team | first group (type, dist) | first hit r | champs on it (first-choosers / all hitters) | kill r | capture r | capturers (n, gems each) | spread r10 | distinct first targets | attack range (tiles:count) | side |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for m in maps:
    for t in ['mite','uni']:
        rows = [d for d in D if d['map']==m and d['team']==t]
        fc = [d['first_camp'] for d in rows]
        types = collections.Counter('%s d%s' % ('+'.join(x['types']), x['dist']) for x in fc)
        rc = collections.Counter(); sc = collections.Counter()
        for x in fc:
            for k,v in x['range_counts'].items(): rc[k]+=v
            for k,v in x['side_counts'].items(): sc[k]+=v
        caps = collections.Counter('%d x %s' % (len(x['capturers']), '/'.join(str(g) for g in x['cap_gems'])) for x in fc)
        print('| %s | %s | %s | %s | %s / %s | %s | %s | %s | %s | %s | %s | %s |' % (m, t, ', '.join('%s (%d)'%(k,v) for k,v in types.items()),
            rng([x['first_hit'] for x in fc]), rng([x['n_first_choosers'] for x in fc]), rng([x['n_hitters'] for x in fc]), rng([x['killed'] for x in fc]), rng([x['captured'] for x in fc]),
            ', '.join('%s (%d)'%(k,v) for k,v in caps.items()), rng([d['spread'].get('10') for d in rows]), rng([d['n_distinct_first_groups'] for d in rows]),
            ' '.join('%s:%d'%(k,v) for k,v in sorted(rc.items())), ' '.join('%s:%d'%(k[:5],v) for k,v in sc.items())))
print()
print('## B. first tribute / recalls / captures by r60')
print('| map | team | first tribute r | altar | bag | who | tributes by r60 (n games with >=1) | recalls by r60 per game | captures by r60 per game | gems carried+tributed r60 |')
print('|---|---|---|---|---|---|---|---|---|---|')
for m in maps:
    for t in ['mite','uni']:
        rows = [d for d in D if d['map']==m and d['team']==t]
        ft = [d['first_tribute'] for d in rows]
        who = collections.Counter(x[1][:4] if x else 'none' for x in ft)
        alt = collections.Counter(x[3] if x else 'none' for x in ft)
        print('| %s | %s | %s | %s | %s | %s | %d/6 | %s | %s | %s |' % (m, t, rng([x[0] for x in ft if x]) if any(ft) else 'none by r70', ', '.join('%s(%d)'%(k,v) for k,v in alt.items()),
            rng([x[2] for x in ft if x]), ', '.join('%s(%d)'%(k,v) for k,v in who.items()), sum(1 for d in rows if any(x[0]<=60 for x in d['tributes'])),
            rng([len(d['recalls']) for d in rows]), rng([len(d['captures']) for d in rows]), rng([d['gems_r60']['carried']+d['gems_r60']['sub'] for d in rows])))
print()
print('## C. fight maps: centre, contact, first fight')
print('| map | team | game | opp | centre arrival r (who) | captures before contact | first contact r (who, kind) | contact pos dist-to-centre | fight window | my deaths | enemy deaths | deaths by r60 | result |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for m in ['collision','corners','elkring','interlock','packs','lanes']:
    for t in ['mite','uni']:
        for d in [d for d in D if d['map']==m and d['team']==t]:
            c = d['first_contact']; ca = d['centre_arrival']
            nb = sum(1 for x in d['captures'] if c is None or x[0] < c['r'])
            print('| %s | %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %d | %s |' % (m, t, d['match'][:8], d['opp'][:12], ('r%d %s'%(ca[0],ca[1])) if ca else '-', nb,
                ('r%d %s %s'%(c['r'],c['who'],c['kind'].replace('hit_','')) if c else 'none<r70'), (c['dcentre'] if c and c['dcentre']<1000 else '-') if c else '-',
                ('r%d-%d'%(c['r'],c['end'])) if c else '-', len(c['my_deaths']) if c else '-', len(c['enemy_deaths']) if c else '-', len(d['deaths60']), d['res']))
