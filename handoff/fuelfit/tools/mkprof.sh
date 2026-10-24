#!/bin/bash
# mkprof.sh NAME : kvdet8 + opts + ungate + autoprof -> ws/bots/NAME
set -e; V=$(dirname $0); rm -rf $V/ws/bots/$1; mkdir -p $V/ws/bots/$1; $V/applyopts.sh $V/kvdet8/src $V/ws/bots/$1/src
python3 $V/ungate.py $V/ws/bots/$1/src/main.cpp; python3 $V/autoprof.py $V/ws/bots/$1/src >/dev/null; python3 $V/profhdr.py $V/ws/bots/$1/src/main.cpp
sed -i 's/const bool big_ = used > 70000;/const bool big_ = used > 92000;/' $V/ws/bots/$1/src/main.cpp
