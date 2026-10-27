cd /tmp/claude-0/w/ws
for c in "$@"; do for r in kvvl e1f rHunt rTop1 rD; do bash bench.sh $c $r ${c}_$r; rm -rf rep/${c}_$r; done; done > res/full4_$1.txt 2>&1
