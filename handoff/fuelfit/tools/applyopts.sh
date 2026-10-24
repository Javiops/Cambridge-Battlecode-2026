#!/bin/bash
# applyopts.sh BASESRC OUTSRC : copy and apply opts/o*.py in order
set -e; V=$(dirname $0); rm -rf $2; cp -r $1 $2; for o in $V/opts/o*.py; do python3 $o $2; done
