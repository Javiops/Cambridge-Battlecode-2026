"""Start unranked challenges with our ACTIVE bot (needs the browser session cookie, see README).
Usage: python3 challenge.py [--top N] [--targets name1,name2] [--maps rows,corners,...] [--max K] [--dry-run]
Picks the opponents we have played least recently among the top N (default 20) that the site lets us challenge, and
spends up to K of the remaining hourly allowance (default: all of it)."""
import json, os, sys, time
from common import *
args = sys.argv[1:]
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default
cookie = session_cookie()
if not cookie: sys.exit('no session cookie: set CAMBC_COOKIE or write it to ~/.cambc_cookie (see README.md)')
state = api('/challenges', cookie=cookie)
quota = state.get('quota') or {}; left = max(0, (quota.get('limit') or 0) - (quota.get('used') or 0))
log(f"challenge: quota {quota.get('used')}/{quota.get('limit')} used, resets {quota.get('resetsAt')}, rank {state.get('requesterRank')}, max gap {state.get('maxRankGap')}, maps {len(state.get('maps') or [])}")
if not state.get('ready'): sys.exit('site says not ready (no active bot?)')
maxk = int(opt('--max', left)); left = min(left, maxk)
if left <= 0: log('nothing to do: allowance used'); sys.exit(0)
ladder = api('/ladder')['teams']; byname = {t['name']: t for t in ladder}
top = int(opt('--top', 20)); targets = opt('--targets')
cands = [byname[n] for n in targets.split(',') if n in byname] if targets else [t for t in ladder if t['rank'] <= top]
ranks = state.get('opponentRanks') or {}; gap = state.get('maxRankGap'); me = state.get('requesterRank') or 0
ok = []
for t in cands:
    if t['teamId'] == US or not t.get('hasBot'): continue
    r = ranks.get(t['teamId'], t['rank'])
    if gap is not None and r is not None and r < me - gap: continue      # outside the allowed rank range
    ok.append(t)
# least recently played first
games = load_jsonl(os.path.join(DATA, 'games.jsonl')); last = {}
for g in games: last[g['opp_id']] = max(last.get(g['opp_id'], ''), g['at'])
ok.sort(key=lambda t: last.get(t['teamId'], ''))
maps_sel = None
if opt('--maps'):
    known = {m['name'].lower(): m['id'] for m in state.get('maps') or [] if 'name' in m and 'id' in m}
    maps_sel = [known[n.strip().lower()] for n in opt('--maps').split(',') if n.strip().lower() in known]
started = 0
for t in ok[:left]:
    body = {'mapIds': maps_sel} if maps_sel else {}
    if '--dry-run' in args: log(f"would challenge {t['name']} (rank {t['rank']}) {body}"); continue
    try:
        r = api('/challenges', method='POST', body={'teamId': t['teamId'], **body}, cookie=cookie)
        log(f"started vs {t['name']} (rank {t['rank']}): group {r.get('groupId')}"); started += 1
        with open(os.path.join(DATA, 'challenges.jsonl'), 'a') as f: f.write(json.dumps(dict(at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), opp=t['name'], opp_id=t['teamId'], group=r.get('groupId'), maps=maps_sel)) + '\n')
    except Exception as e:
        log(f"failed vs {t['name']}: {e}")
        if '429' in str(e) or 'allowance' in str(e).lower(): break
    time.sleep(2)
log(f'challenge: started {started}')
