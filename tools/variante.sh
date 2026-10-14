#!/bin/bash
# Crea una variante de un bot cambiando interruptores de params.h y la compila.
# uso: tools/variante.sh NUEVO BASE "#define P_FINISH 40\n#define P_UNI_FLEE 45"
# Ejemplo: tools/variante.sh prueba1 v30 "#define P_FINISH 40"
# Los interruptores que ya estén en params.h de BASE se quitan antes de añadir los nuevos.
set -e
cd "$(dirname "$0")/.."
NEW=$1; BASE=$2; DEFS=$3
[ -n "$NEW" ] && [ -n "$BASE" ] || { echo "uso: $0 NUEVO BASE \"#define ...\""; exit 1; }
mkdir -p "bots/$NEW/src"
cp "bots/$BASE/src/main.cpp" "bots/$BASE/src/fight.h" "bots/$BASE/src/params.h" "bots/$NEW/src/"
for n in $(printf "%b\n" "$DEFS" | awk '/#define/{print $2}'); do sed -i.bak "/#define $n /d" "bots/$NEW/src/params.h"; done
rm -f "bots/$NEW/src/params.h.bak"
printf "%b\n" "$DEFS" >> "bots/$NEW/src/params.h"
cambc build "bots/$NEW"
