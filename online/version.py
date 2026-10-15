#!/usr/bin/env python3
"""Record which version is active on the site (data/versions.jsonl): report.py and lfl.py read it to label the games.

usage:  python3 version.py "v38 = study29 (I012)" [--at 2026-10-15T21:30Z] [--note "activated by Javi"]
Run it right after activating the bot on the site; games from that time on are attributed to that label.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('CAMBC_ONLINE_DATA', os.path.join(HERE, 'data'))
args = sys.argv[1:]
if not args or args[0].startswith('-'):
    sys.exit(__doc__)
at = args[args.index('--at') + 1] if '--at' in args else time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
note = args[args.index('--note') + 1] if '--note' in args else ''
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, 'versions.jsonl'), 'a') as f:
    f.write(json.dumps({'at': at, 'version': args[0], 'note': note}) + '\n')
print(f'{at}  {args[0]}')
