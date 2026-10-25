# fuelfit o47 v2: P_FARM_PD_PER_TURN 1 (one reverse field per choose_target call while they are missing; o45's forward
# search decides meanwhile, same decisions) and the o48 farm warm-up tables built in the start-up turn.
# (v1 text follows) integration of o45 with the step start-up, changes only when the champion starts playing on maps where
# the fields are costly): the reverse group fields (o45) are a start-up step priced 32k each (a compute of the whole 100x100 map is
# 30.6k + 1.2k roots), at most two start-up turns; whatever is left is computed one per choose_target call
# (P_FARM_PD_PER_TURN 1) with the original forward search deciding until all are ready (same decisions, o45).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("#define P_FARM_PD_PER_TURN 1000000  // fuelfit o45","#define P_FARM_PD_PER_TURN 1  // fuelfit o47: one per choose_target call once playing; the start-up does the first ones. o45")
rep("bool init(State& s, bc::champion& me) {\n    if (s.init_stage == 0) {","bool farm_warmup(State& s, int quota);  // fuelfit o48\nbool init(State& s, bc::champion& me) {\n    if (s.init_stage == 0) {")
rep("        s.play_from = s.groups.size() <= INIT_SMALL ? 2 : 3;\n        s.init_stage = 5;","        farm_warmup(s, 1000000);  // fuelfit o47/o48: the farm tables (2.5k + 600 per group) in the start-up turn too\n        s.play_from = s.groups.size() <= INIT_SMALL ? 2 : 3;\n        s.init_stage = 5;")
rep("constexpr std::size_t INIT_SMALL = 14;","""constexpr std::size_t INIT_SMALL = 14;
bool farm_pd_ready(State& s);  // fuelfit o45, defined with choose_target
// fuelfit o47 v3: the idle round of big maps (o08 v3) computes reverse group fields (o45), priced 1.2k + 2.5 fuel per
// map tile each (measured 3.4k on 41x41, 30.6k on 100x100), while they fit 70k; the rest go one per choose_target call.
void init_wait(State& s) {
    const long price = 1200 + (static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) * 5) / 2;
    long left = 70000;
    while (left >= price && s.pd_rf_done < s.groups.size()) {
        const std::size_t before = s.pd_rf_done;
        farm_pd_ready(s);
        left -= price;
        if (s.pd_rf_done == before) break;
    }
}""")
open(p,'w',newline='').write(s)
