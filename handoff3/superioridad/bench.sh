# bench.sh A B TAG: A vs B on all 70 maps, both sides -> res/TAG.txt (lines: map side winner)
A=$1; B=$2; T=$3; mkdir -p res rep/$T; : > rep/$T/m.txt
for m in maps/*.map26a; do n=$(basename $m .map26a); echo "$PWD/bots/$A $PWD/bots/$B $PWD/$m $PWD/rep/$T/${n}_a.repl26a" >> rep/$T/m.txt; echo "$PWD/bots/$B $PWD/bots/$A $PWD/$m $PWD/rep/$T/${n}_b.repl26a" >> rep/$T/m.txt; done
/tmp/claude-0/w/cv4/bin/cambc run-batch --release --jobs 4 rep/$T/m.txt > res/$T.log 2>&1
python3 score.py "$A" "$B" res/$T.log
