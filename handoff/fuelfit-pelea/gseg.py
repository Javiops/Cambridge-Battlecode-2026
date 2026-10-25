# gseg.py MAIN K THR SPEC : segment costs inside section K (prof2 build), over turns whose section K > THR.
# SPEC = python file defining marks = [(anchor, id, 'before'|'after')]
import sys
p,K,thr,spec=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]; s=open(p).read()
ns={}; exec(open(spec).read(),ns); marks=ns['marks']
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
hdr='''double g_gsT[64], g_gsA[64], g_gsB[64]; int g_gsN = 0, g_gsBN = 0; int g_gsLast = -1; std::uint64_t g_gsF = 0;
inline void gseg(int i) { const std::uint64_t f = bc::fuel_remaining(); if (g_gsLast >= 0) g_gsT[g_gsLast] += double(g_gsF) - double(f); g_gsLast = i; g_gsF = bc::fuel_remaining(); }
'''
rep("inline void pf_mark(int i) {", hdr+"inline void pf_mark(int i) { if (g_gsLast >= 0) { gseg(-1); g_gsLast = -1; }")
rep("    const int rr = static_cast<int>(bc::round_number());\n    if (rr % 100 == 0) {\n        std::printf(\"[usec]",
 "    if (g_turn > 1) { const bool b_ = g_tsec[%d] > %s; ++g_gsN; if (b_) ++g_gsBN; for (int k = 0; k < 64; ++k) { g_gsA[k] += g_gsT[k]; if (b_) g_gsB[k] += g_gsT[k]; } }\n    for (int k = 0; k < 64; ++k) g_gsT[k] = 0;\n    const int rr = static_cast<int>(bc::round_number());\n    if (rr %% 100 == 0) {\n        std::printf(\"[gsg] r%%d %%d %%d\", rr, g_gsN, g_gsBN); for (int k = 0; k < 64; ++k) if (g_gsA[k] != 0) std::printf(\" %%d:%%.0f:%%.0f\", k, g_gsA[k], g_gsB[k]); std::printf(\"\\n\");\n        std::printf(\"[usec]" % (K,thr))
import glob,os
files={p:s}
for h in glob.glob(os.path.dirname(p)+'/*.h'): files[h]=open(h).read()
for a,i,w in marks:
    hit=[f for f,t in files.items() if a in t]
    assert len(hit)==1 and files[hit[0]].count(a)==1,(a,hit)
    t=files[hit[0]]
    if w=='repl': t=t.replace(a,i)
    else: t=t.replace(a, a+f'gseg({i});\n' if w=='after' else f'gseg({i});\n'+a)
    files[hit[0]]=t
for f,t in files.items(): open(f,'w').write(t)
