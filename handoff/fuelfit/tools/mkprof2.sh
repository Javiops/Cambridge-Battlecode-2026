#!/bin/bash
# mkprof2.sh SRC NAME : SRC (kvvl-based, e.g. kopt/src) + prof2 + autoprof + profhdr -> ws/bots/NAME (run with --fuel-quantum 2000000)
set -e; V=$(dirname $0); rm -rf $V/ws/bots/$2; mkdir -p $V/ws/bots/$2; cp -r $1 $V/ws/bots/$2/src
python3 $V/prof2.py $V/ws/bots/$2/src/main.cpp; python3 $V/autoprof.py $V/ws/bots/$2/src >/dev/null
python3 - $V/ws/bots/$2/src/main.cpp <<'PY'
import sys
p=sys.argv[1]; s=open(p,newline='').read()
hdr='''double g_prA[400], g_prB[400], g_prT[400], g_prXA[400], g_prXB[400], g_prX[400]; int g_prBigN = 0, g_prAllN = 0; int g_prCur = -1;
struct ProfScope { int id, par; std::uint64_t f0; explicit ProfScope(int i) : id(i), par(g_prCur), f0(cambc::fuel_remaining()) { g_prCur = i; } ~ProfScope() { const double c = double(f0) - double(cambc::fuel_remaining()); g_prT[id] += c; g_prX[id] += c; if (par >= 0) g_prX[par] -= c; g_prCur = par; } };
#define PROF_SCOPE(i) ProfScope prof_scope_{i}
'''
i=s.index("namespace {"); s=s[:i]+hdr+s[i:]
a="    const int rr = static_cast<int>(bc::round_number());\n    if (rr % 100 == 0) {\n        std::printf(\"[usec]"
assert s.count(a)==1
s=s.replace(a,"""    if (g_turn > 1) { const bool big_ = used > 92000; ++g_prAllN; if (big_) ++g_prBigN; for (int k = 0; k < 400; ++k) { g_prA[k] += g_prT[k]; g_prXA[k] += g_prX[k]; if (big_) { g_prB[k] += g_prT[k]; g_prXB[k] += g_prX[k]; } } }
    for (int k = 0; k < 400; ++k) g_prT[k] = g_prX[k] = 0;
"""+a)
b='        std::printf("[ugh] r%d", rr);'
s=s.replace(b,'        std::printf("[prf] r%d %d %d", rr, g_prAllN, g_prBigN); for (int k = 0; k < 400; ++k) if (g_prA[k] != 0) std::printf(" %d:%.0f:%.0f:%.0f:%.0f", k, g_prA[k], g_prB[k], g_prXA[k], g_prXB[k]); std::printf("\\n");\n'+b,1)
open(p,'w',newline='').write(s)
PY
