#!/bin/bash
# ab.sh A B 'MAPGLOB' TAG -> log out/TAG.log, prints summary + sign test
cd /home/user/ws
python3 tools/arena.py bots/$1 bots/$2 --maps "$3" --sides both --jobs 4 --no-build --out out/$4 > out/$4.log 2>&1
tail -1 out/$4.log
python3 tools/sign.py out/$4.log
python3 - out/$4.log <<'PY'
import re,sys
s=0
for l in open(sys.argv[1]):
    m=re.search(r'gems\s+(\d+)-\s*(\d+)',l)
    if m: s+=int(m[1])-int(m[2])
print('total gem diff', s)
PY
