# mk.sh NAME OPT [DEFINES...]: copy E1 to bots/NAME, apply opt, add defines on top of params.h
set -e
N=$1; O=$2; shift 2
rm -rf bots/$N; mkdir -p bots/$N; (cd bots/$N && unzip -oq /tmp/claude-0/w/assets/pcassets/zips/${BASE:-e1}.zip)
[ "$O" != "-" ] && python3 /tmp/claude-0/w/opts/$O.py bots/$N/src
for d in "$@"; do k=${d%%=*}; v=${d#*=}; sed -i "1i #define $k $v" bots/$N/src/params.h; done
/tmp/claude-0/w/cv4/bin/cambc build --release bots/$N 2>&1 | tail -1
