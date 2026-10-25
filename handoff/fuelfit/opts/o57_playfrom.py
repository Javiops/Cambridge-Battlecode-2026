# fuelfit o57 (first playing round by a start-up cost model; replaces o08 v3's "<= 14 groups" rule). Start-up measured
# on the 40 maps with unlimited fuel (tools/heavy.py): cost_k ~ 68 + 18 * tiles/1000 + 5 * groups (least squares; worst
# residual +31k). Rounds the start-up needs: 1 if est <= 186k, else 1 + ceil((est - 186k) / 86k); the champion plays
# from the next round. Small maps (<= 14 groups and <= 3000 tiles, all measured <= 174k) keep round 2 as before. On
# big_world (373k) the old rule said round 3 while start-up really ended in round 4: the first moves then depended on
# the fuel (probe divergences at r11 on far maps).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="        s.play_from = s.groups.size() <= INIT_SMALL ? 2 : 3;\n"
assert s.count(a)==1
s=s.replace(a,"""        {  // fuelfit o57: first playing round from the start-up cost model (see opts/o57_playfrom.py)
            const long tiles = static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height());
            const long est = 68000 + 18 * tiles + 5000 * static_cast<long>(s.groups.size()) + 20000;
            int rounds = est <= 186000 ? 1 : 1 + static_cast<int>((est - 186000 + 85999) / 86000);
            if (s.groups.size() <= INIT_SMALL && tiles <= 3000) rounds = 1;
            s.play_from = rounds + 1;
        }
""")
open(p,'w',newline='').write(s)
