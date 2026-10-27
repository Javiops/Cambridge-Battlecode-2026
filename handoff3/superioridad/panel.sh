cd /tmp/claude-0/w/ws
for c in "$@"; do for r in rHunt rTop1 rD; do bash bench.sh $c $r ${c}_$r; rm -rf rep/${c}_$r; done; done > res/panel_$1.txt 2>&1
