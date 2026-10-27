# h2h.sh A B TAG: A vs B on all 70 maps, both sides
A=$1; B=$2; T=$3; cd /tmp/claude-0/w/ws; mkdir -p res rep/$T; : > rep/$T/m.txt
for m in maps/*.map26a; do n=$(basename $m .map26a); echo "$PWD/bots/$A $PWD/bots/$B $PWD/$m $PWD/rep/$T/${n}_a.repl26a" >> rep/$T/m.txt; echo "$PWD/bots/$B $PWD/bots/$A $PWD/$m $PWD/rep/$T/${n}_b.repl26a" >> rep/$T/m.txt; done
../cv4/bin/cambc run-batch --release --jobs 4 rep/$T/m.txt > res/$T.log 2>&1
