# fuelfit o62 (exact, after o60): the recall home field (cr_return_walk computes cr_home_df on its first call, 26-31k on
# 100x100, in the first playing turn) is built in the idle round of big maps when it fits, right after the o60 prefill.
# Same compute, same inputs (spawn and static walls), so the same field.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""            s.pd_fwd_round = s.play_from;  // the first playing turn counts as having paid its field: no o54 warm-up there
        }
    }
""","""            s.pd_fwd_round = s.play_from;  // the first playing turn counts as having paid its field: no o54 warm-up there
        }
    }
    if (!s.cr_home_ready && left >= price) {  // fuelfit o62: the recall home field (cr_return_walk's first call)
        s.cr_home_ready = attempt([&] {
            bc::bitboard roots = s.my_spawn & ~s.static_block;
            s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
            return true;
        });
        left -= price;
    }
""")
open(p,'w',newline='').write(s)
