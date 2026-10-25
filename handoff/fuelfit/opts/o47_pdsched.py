# fuelfit o47 (integration of o45 with the step start-up, changes only when the champion starts playing on maps where
# the fields are costly): the reverse group fields (o45) are a start-up step priced 32k each (a compute of the whole 100x100 map is
# 30.6k + 1.2k roots), at most two start-up turns; whatever is left is computed one per choose_target call
# (P_FARM_PD_PER_TURN 1) with the original forward search deciding until all are ready (same decisions, o45).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("#define P_FARM_PD_PER_TURN 1000000  // fuelfit o45","#define P_FARM_PD_PER_TURN 1  // fuelfit o47: one per choose_target call once playing; the start-up does the first ones. o45")
rep("    std::size_t init_gi = 0;\n","    std::size_t init_gi = 0;\n    int init_pd_turns = 0;  // fuelfit o47: start-up turns spent on the reverse group fields (max 2)\n")
rep("constexpr long INIT_C_MAP = 56000,","bool farm_pd_ready(State& s);  // fuelfit o47 (defined with choose_target)\nconstexpr long INIT_C_PD = 32000, INIT_PD_TURNS = 2;  // 30.6k compute on 100x100 + roots/and-not 1.2k\nconstexpr long INIT_C_MAP = 56000,")
rep("""        if (s.dash_slot >= 0) mp_find_dashholes(s);
        s.init_stage = 5;
    }
    return true;
}""","""        if (s.dash_slot >= 0) mp_find_dashholes(s);
        left -= INIT_C_DASH;
        s.init_stage = 5;
    }
    if (s.init_stage == 5) {  // fuelfit o47: reverse group fields, as many as fit, at most INIT_PD_TURNS turns
        if (s.init_pd_turns < INIT_PD_TURNS && s.pd_rf_done < s.groups.size()) {
            if (left < INIT_C_PD) return false;  // a fresh turn for them
            ++s.init_pd_turns;
            while (left >= INIT_C_PD && s.pd_rf_done < s.groups.size()) {
                const std::size_t before = s.pd_rf_done;
                farm_pd_ready(s);
                left -= INIT_C_PD;
                if (s.pd_rf_done == before) break;  // an SDK failure: choose_target retries later
            }
            if (s.init_pd_turns < INIT_PD_TURNS && s.pd_rf_done < s.groups.size()) return false;
        }
        s.init_stage = 6;
    }
    return true;
}""")
open(p,'w',newline='').write(s)
