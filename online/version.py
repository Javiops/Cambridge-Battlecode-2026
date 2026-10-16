#!/usr/bin/env python3
"""Record which version is active on the site (data/versions.jsonl): report.py and lfl.py read it to label the games.

usage:  python3 version.py "v38 = study29 (I012)" --zip /mnt/project-files/bot/mybot_I012.zip [--at 2026-10-15T21:30Z] [--note "activated by Javi"]
Run it right after activating the bot on the site; games from that time on are attributed to that label.
--zip is the exact zip that was uploaded: its path, sha256 and source hash are stored, so the local gate can play
against the online bot itself (`tools/gate.py bots/X online`) and tell when its base is not the online bot.
"""
import hashlib, json, os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import online_base  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('CAMBC_ONLINE_DATA', os.path.join(HERE, 'data'))
args = sys.argv[1:]
if not args or args[0].startswith('-'):
    sys.exit(__doc__)
at = args[args.index('--at') + 1] if '--at' in args else time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
note = args[args.index('--note') + 1] if '--note' in args else ''
row = {'at': at, 'version': args[0], 'note': note}
if '--zip' in args:
    z = os.path.abspath(args[args.index('--zip') + 1])
    if not os.path.exists(z):
        sys.exit(f'{z}: no such zip')
    row |= {'zip': z, 'zip_sha256': hashlib.sha256(open(z, 'rb').read()).hexdigest(), 'src_sha': online_base.src_hash(z)}
else:
    print('warning: no --zip: the gate will not be able to check that its base is this version', file=sys.stderr)
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, 'versions.jsonl'), 'a') as f:
    f.write(json.dumps(row) + '\n')
print(f'{at}  {args[0]}' + (f'  src {row["src_sha"][:10]}' if 'src_sha' in row else ''))
