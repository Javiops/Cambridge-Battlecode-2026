import sys
p=sys.argv[1]; s=open(p).read()
a="    if (g_turn > 1) for (int k = 0; k < 14; ++k) { int b_ = static_cast<int>(g_tsec[k] / 2500);"
assert s.count(a)==1
s=s.replace(a,"    if (g_turn > 1) for (int k : {0, 5, 8, 9, 12}) { int b_ = static_cast<int>(g_tsec[k] / 1000); if (b_ > 99) b_ = 99; ++g_fh[k][b_]; }\n"+a)
s=s.replace("inline void pf_mark(int i) {","int g_fh[14][100];\ninline void pf_mark(int i) {",1)
b='        std::printf("[ugh] r%d", rr);'
s=s.replace(b,'        for (int k : {0, 5, 8, 9, 12}) { std::printf("[ufh] %d", k); for (int b_ = 0; b_ < 100; ++b_) std::printf(" %d", g_fh[k][b_]); std::printf("\\n"); }\n'+b,1)
open(p,'w').write(s)
