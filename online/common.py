"""Shared helpers for the online testing loop (stdlib only, Python 3.9+)."""
import json, os, sys, time, urllib.request, urllib.error
BASE = 'https://2026a.battlecode.co.uk'
US = '292625c5-0f3a-49f0-a08a-9757b8f58658'          # our team id ("Live Love Larp")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
def session_cookie():
    """The browser session: env CAMBC_COOKIE, else the file named by CAMBC_COOKIE_FILE, else ~/.cambc_cookie."""
    c = os.environ.get('CAMBC_COOKIE')
    if c: return c.strip()
    for p in (os.environ.get('CAMBC_COOKIE_FILE'), os.path.expanduser('~/.cambc_cookie')):
        if p and os.path.exists(p): return open(p).read().strip()
    return None
def api(path, method='GET', body=None, cookie=None, tries=4):
    """One polite call: sequential, backs off on 429/5xx, returns parsed JSON (or raises)."""
    url = BASE + '/api/v1' + path
    data = json.dumps(body).encode() if body is not None else None
    hdr = {'accept': 'application/json', 'user-agent': 'cambc-online-loop/1 (team Live Love Larp)'}
    if data is not None: hdr['content-type'] = 'application/json'
    if cookie: hdr['cookie'] = cookie; hdr['origin'] = BASE; hdr['referer'] = BASE + '/game/matches'
    for a in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, method=method, headers=hdr), timeout=60)
            return json.loads(r.read() or b'null')
        except urllib.error.HTTPError as e:
            txt = e.read()[:300].decode(errors='replace')
            if e.code == 429:
                ra = e.headers.get('Retry-After'); wait = int(ra) if ra and ra.isdigit() else 60
                log(f'429 on {path}, waiting {wait}s'); time.sleep(min(wait, 600)); continue
            if e.code >= 500 and a < tries - 1: log(f'{e.code} on {path}, retry'); time.sleep(5 * (a + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code} {txt}')
        except (urllib.error.URLError, TimeoutError) as e:
            if a < tries - 1: time.sleep(5 * (a + 1)); continue
            raise
def log(msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()) + ' ' + msg
    print(line, flush=True)
    with open(os.path.join(DATA, 'loop.log'), 'a') as f: f.write(line + '\n')
def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
