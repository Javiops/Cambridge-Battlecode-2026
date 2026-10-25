# fuelfit o16 (pelea and others): my_roster / en_roster returned a copy of the cached roster vector (an allocation plus
# one heavy bc::champion copy per champion) on every call, ~10 call sites, several per turn (pe_update every turn of
# the pf window). They now return a const reference to the roster, which is filled once per game and never changed,
# and the read-only callers bind it by const reference. Same champions, same order: exact.
import sys,re,glob,os
d=sys.argv[1]
fs=[d+'/main.cpp']+glob.glob(d+'/*.h')
for p in fs:
    s=open(p,newline='').read(); o=s
    s=s.replace("inline std::vector<bc::champion> my_roster(State& s) {","inline const std::vector<bc::champion>& my_roster(State& s) {  // fuelfit o16: no copy")
    s=s.replace("inline std::vector<bc::champion> en_roster(State& s) {","inline const std::vector<bc::champion>& en_roster(State& s) {  // fuelfit o16: no copy")
    s=s.replace("auto allies = my_roster(s);","const auto& allies = my_roster(s);  // fuelfit o16")
    s=s.replace("auto roster = en_roster(s);","const auto& roster = en_roster(s);  // fuelfit o16")
    if s!=o: open(p,'w',newline='').write(s)
s=open(d+'/main.cpp').read()
assert s.count("fuelfit o16: no copy")==2
