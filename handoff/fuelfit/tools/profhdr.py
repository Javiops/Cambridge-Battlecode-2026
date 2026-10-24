# profhdr.py MAIN: defines PROF_SCOPE before first use + per-turn accounting (needs ungate.py's dm_turn_end)
import sys
p=sys.argv[1]; s=open(p).read()
hdr='''double g_prA[400], g_prB[400], g_prT[400], g_prXA[400], g_prXB[400], g_prX[400]; int g_prBigN = 0, g_prAllN = 0; int g_prCur = -1;
struct ProfScope { int id, par; std::uint64_t f0; explicit ProfScope(int i) : id(i), par(g_prCur), f0(cambc::fuel_remaining()) { g_prCur = i; } ~ProfScope() { const double c = double(f0) - double(cambc::fuel_remaining()); g_prT[id] += c; g_prX[id] += c; if (par >= 0) g_prX[par] -= c; g_prCur = par; } };
#define PROF_SCOPE(i) ProfScope prof_scope_{i}
'''
a="namespace {"
i=s.index(a); s=s[:i]+hdr+s[i:]
b="""    for (int k = 0; k < 30; ++k) g_tsec[k] = 0;
}"""
assert s.count(b)==1
s=s.replace(b,"""    for (int k = 0; k < 30; ++k) g_tsec[k] = 0;
    if (g_dm_turn > 1) { const bool big_ = used > 70000; ++g_prAllN; if (big_) ++g_prBigN; for (int k = 0; k < 400; ++k) { g_prA[k] += g_prT[k]; g_prXA[k] += g_prX[k]; if (big_) { g_prB[k] += g_prT[k]; g_prXB[k] += g_prX[k]; } } }
    for (int k = 0; k < 400; ++k) g_prT[k] = g_prX[k] = 0;
}""")
c='std::printf("[ugh] r%d", rr);'
s=s.replace(c,'std::printf("[prf] r%d %d %d", rr, g_prAllN, g_prBigN); for (int k = 0; k < 400; ++k) if (g_prA[k] != 0) std::printf(" %d:%.0f:%.0f:%.0f:%.0f", k, g_prA[k], g_prB[k], g_prXA[k], g_prXB[k]); std::printf("\\n"); '+c)
open(p,'w').write(s)
