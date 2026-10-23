#!/usr/bin/env python3
"""Which bot is online, as source code: the base the local gate has to beat.

`online/version.py "<label>" --zip <uploaded zip>` records, next to the label, the zip's path and a hash of its source
files. This module reads that record back:

  python3 tools/online_base.py                 # the active version, its zip and source hash
  python3 tools/online_base.py bots/X          # is bots/X the bot that is online? (exit 0 yes, 1 no, 2 unknown)

gate.py uses it in two ways: `gate.py bots/CAND online` plays against the recorded zip itself, and every gate run says
whether its base is the online bot (a PASS against anything else does not clear an upload).
The source hash covers the names and bytes of the C/C++ sources and headers only (src/ prefix dropped, CRLF -> LF, junk such
as __MACOSX, dotfiles, *.bak or cambc.toml ignored), so the same code bundled twice, zipped on Windows or exported from git
gives the same hash; the zip's own sha256 is kept too. Records made with the older every-file hash are still recognised.
"""
import glob, hashlib, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIRS = [os.environ.get('CAMBC_ONLINE_DATA', ''), os.path.join(HERE, '..', 'online', 'data'),
             '/mnt/project-files/online/data']


SRC_EXT = ('.cpp', '.cc', '.cxx', '.c', '.h', '.hh', '.hpp', '.hxx', '.inl', '.ipp')


def _keep(name):
    """A bot source file: a C/C++ source or header, not packaging junk (__MACOSX, dotfiles, *.bak, *.orig, cambc.toml)."""
    parts = name.replace('\\', '/').split('/')
    if any(p.startswith('.') or p == '__MACOSX' for p in parts):
        return False
    return name.lower().endswith(SRC_EXT)


def _norm(data):
    """Same bytes whichever OS packed it: CRLF -> LF (git autocrlf on Windows), no UTF-8 BOM."""
    if data.startswith(b'\xef\xbb\xbf'):
        data = data[3:]
    return data.replace(b'\r\n', b'\n')


def src_files(path, legacy=False):
    """{relative name: bytes} of the bot sources in a bot folder, a src folder or a zip (the src/ prefix is dropped).

    Only C/C++ sources and headers count, with line endings normalised, so the same code zipped on Windows, zipped
    with extra files (README, cambc.toml, __MACOSX) or exported from git hashes the same. legacy=True = the rule used
    before 2026-10-16 15:10 (every file, raw bytes), kept to read src_sha values recorded with it."""
    out = {}
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if not n.endswith('/')]
            for n in names:
                key = n.split('src/', 1)[1] if 'src/' in n else os.path.basename(n)
                if legacy:
                    out[key] = z.read(n)
                elif _keep(n):
                    out[key] = _norm(z.read(n))
        return out
    root = os.path.join(path, 'src') if os.path.isdir(os.path.join(path, 'src')) else path
    for f in glob.glob(os.path.join(root, '**', '*'), recursive=True):
        if os.path.isfile(f) and '.cambc' not in f:
            key = os.path.relpath(f, root).replace(os.sep, '/')
            if legacy:
                out[key] = open(f, 'rb').read()
            elif _keep(key):
                out[key] = _norm(open(f, 'rb').read())
    return out


def src_hash(path, legacy=False):
    h = hashlib.sha256()
    for name, data in sorted(src_files(path, legacy).items()):
        h.update(name.encode() + b'\0' + hashlib.sha256(data).digest())
    return h.hexdigest()


def versions_file():
    for d in DATA_DIRS:
        if d and os.path.exists(os.path.join(d, 'versions.jsonl')):
            return os.path.join(d, 'versions.jsonl')
    return None


def active():
    """The record of versions.jsonl with the latest time (the version online now), or None.

    By time, not by line order: rows are sometimes appended late (on 16 Oct a 12:52:00 note without --zip was written
    after the 12:52:59 row that has the zip, and "last line" made the gate lose track of the online source)."""
    f = versions_file()
    if not f:
        return None
    rows = [json.loads(l) for l in open(f) if l.strip()]
    if not rows:
        return None
    return max(enumerate(rows), key=lambda ir: ((ir[1].get('at') or ir[1].get('from') or '')[:19], ir[0]))[1]


def check(base):
    """(True|False|None, message): is `base` the source of the active online version? None = cannot tell."""
    a = active()
    if not a:
        return None, 'no online/data/versions.jsonl here: cannot tell whether the base is the online bot'
    if not a.get('src_sha'):
        return None, (f'the online version "{a.get("version")}" was recorded without --zip: cannot tell whether the base '
                      'is the online bot (record it again with online/version.py --zip)')
    mine = src_hash(base)
    if a['src_sha'] in (mine, src_hash(base, legacy=True)):
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
    if a.get('src_sha') and a['src_sha'] not in (src_hash(a['zip']), src_hash(a['zip'], legacy=True)):
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
