# fuelfit o27 (pelea, contabilidad): income_log / pe_update / pf_log run in run_game right after play_turn and before
# FP(12), so on a turn whose play_turn returned from the fight step they were counted in section 9 (~2k on heavy fight
# turns). They now open the log section (13). FP is a no-op outside the profile builds: exact.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="            play_turn(s);\n            income_log(s);\n"
assert s.count(a)==1
s=s.replace(a,"            play_turn(s);\n            FP(13, \"log\");  // fuelfit o27: the logs below are not part of the fight step\n            income_log(s);\n")
open(p,'w',newline='').write(s)
