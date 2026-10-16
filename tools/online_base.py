#!/usr/bin/env python3
"""Which bot is online, as source code: the base the local gate has to beat.

`online/version.py "<label>" --zip <uploaded zip>` records, next to the label, the zip's path and a hash of its source
files. This module reads that record back:

  python3 tools/online_base.py                 # the active version, its zip and source hash
  python3 tools/online_base.py bots/X          # is bots/X the bot that is online? (exit 0 yes, 1 no, 2 unknown)

gate.py uses it in two ways: `gate.py bots/CAND online` plays against the recorded zip itself, and every gate run says
whether its base is the online bot (a PASS against anything else does not clear an upload).
The source hash covers the file names and bytes under src/ only, so the same code bundled twice (or exported from git)
gives the same hash; the zip's own sha256 is kept too.
"""
import glob, hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIRS = [os.environ.get('CAMBC_ONLINE_DATA', ''), os.path.join(HERE, '..', 'online', 'data'),
             '/mnt/project-files/online/data']


def src_files(path):
    """{relative name: bytes} of the bot sources in a bot folder, a src folder or a zip (the src/ prefix is dropped)."""
    out = {}
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.endswith('/'): continue
                out[n.split('src/', 1)[1] if 'src/' in n else os.path.basename(n)] = z.read(n)
        return out
    root = os.path.join(path, 'src') if os.path.isdir(os.path.join(path, 'src')) else path
    for f in glob.glob(os.path.join(root, '**', '*'), recursive=True):
        if os.path.isfile(f) and '.cambc' not in f:
            out[os.path.relpath(f, root).replace(os.sep, '/')] = open(f, 'rb').read()
    return out


def src_hash(path):
    h = hashlib.sha256()
    for name, data in sorted(src_files(path).items()):
        h.update(name.encode() + b'\0' + hashlib.sha256(data).digest())
    return h.hexdigest()


def versions_file():
    for d in DATA_DIRS:
        if d and os.path.exists(os.path.join(d, 'versions.jsonl')):
            return os.path.join(d, 'versions.jsonl')
    return None


def active():
    """The last record of versions.jsonl (the version online now), or None."""
    f = versions_file()
    if not f:
        return None
    rows = [json.loads(l) for l in open(f) if l.strip()]
    return rows[-1] if rows else None


def check(base):
    """(True|False|None, message): is `base` the source of the active online version? None = cannot tell."""
    a = active()
    if not a:
        return None, 'no online/data/versions.jsonl here: cannot tell whether the base is the online bot'
    if not a.get('src_sha'):
        return None, (f'the online version "{a.get("version")}" was recorded without --zip: cannot tell whether the base '
                      'is the online bot (record it again with online/version.py --zip)')
    mine = src_hash(base)
    if mine == a['src_sha']:
        return True, f'base = the online bot "{a["version"]}" (source hash {mine[:10]})'
    return False, (f'base is NOT the online bot "{a["version"]}" (base source {mine[:10]}, online {a["src_sha"][:10]}): '
                   'a PASS here does not clear an upload; use `online` as the base')


def export():
    """Unpack the active online zip into out/base/online@<hash>/src and return that folder (gate.py's `online` base)."""
    a = active()
    if not a or not a.get('zip'):
        sys.exit('base "online": the active version has no zip on record; run online/version.py "<label>" --zip <zip>')
    if not os.path.exists(a['zip']):
        sys.exit(f'base "online": the recorded zip {a["zip"]} is not on this machine')
    if a.get('src_sha') and src_hash(a['zip']) != a['src_sha']:
        sys.exit(f'base "online": {a["zip"]} changed since it was recorded (source hash differs)')
    dst = os.path.join('out', 'base', f'online@{src_hash(a["zip"])[:10]}')
    if not os.path.isdir(os.path.join(dst, 'src')):
        for name, data in src_files(a['zip']).items():
            p = os.path.join(dst, 'src', name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'wb').write(data)
    print(f'base = the online bot "{a["version"]}" from {a["zip"]} -> {dst}')
    return dst


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ok, msg = check(sys.argv[1])
        print(msg)
        sys.exit({True: 0, False: 1, None: 2}[ok])
    a = active()
    print(json.dumps(a, indent=1) if a else 'no versions.jsonl found')
