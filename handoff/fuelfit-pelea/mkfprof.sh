#!/bin/bash
# mkfprof.sh NAME : kvdet8 + opts + popts + ungate + autoprof (fight-section scopes) + fseg, big = fight > 33k
set -e; S=/tmp/claude-0/-home-user-cambridge-battlecode-2026/51bdd730-0e5e-563f-bd46-0d2623e322d3/scratchpad; W=$S/mech/ws; N=$1
cd $W; rm -rf bots/$N; mkdir -p bots/$N; ./applyopts.sh $S/ff/kvdet8/src bots/$N/src >/dev/null
for o in $S/popts/o*.py; do python3 $o bots/$N/src; done
python3 ungate.py bots/$N/src/main.cpp; python3 autoprof.py bots/$N/src >/dev/null; python3 profhdr.py bots/$N/src/main.cpp
python3 - bots/$N/src/main.cpp <<'PY'
import sys; f=sys.argv[1]; m=open(f).read()
def rep(a,b):
    global m
    assert m.count(a)==1,a; m=m.replace(a,b)
rep("    for (int k = 0; k < 30; ++k) g_tsec[k] = 0;\n    if (g_dm_turn > 1) { const bool big_ = used > 70000;","    const double fsec_ = g_tsec[9];\n    for (int k = 0; k < 30; ++k) g_tsec[k] = 0;\n    if (g_dm_turn > 1) { const bool big_ = fsec_ > 33000;")
rep("int g_prCur = -1;","int g_prCur = -1; int g_prSec = 0;")
rep("g_prT[id] += c; g_prX[id] += c; if (par >= 0) g_prX[par] -= c;","if (g_prSec == 9) { g_prT[id] += c; g_prX[id] += c; if (par >= 0) g_prX[par] -= c; }")
rep("    g_dm_sec = i;\n}","    g_dm_sec = i;\n    g_prSec = i;\n}")
open(f,'w').write(m)
PY
python3 $S/fseg.py bots/$N/src/main.cpp 33000
