#!/bin/bash
# Rebuild a fresh cloud container for the structure GA and resume from the shared checkpoint.
# Usage (repo root): tools/ga/island_restore.sh [SRC]; then restart the level that was running (see run.log there).
set -e
SRC=${1:-/mnt/project-files/ga-farm/islands/structure-sga}
export SSL_CERT_FILE=/root/.ccr/ca-bundle.crt CAMBC_NO_UPDATE_CHECK=1
command -v cambc >/dev/null || pip install -q cambc
C=/root/.cache/cambc; mkdir -p $C
if [ ! -x $C/wasi-sdk-33/bin/clang ]; then
  curl -sSL https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-33/wasi-sdk-33.0-x86_64-linux.tar.gz | { mkdir -p $C/wasi-sdk-33; tar xz -C $C/wasi-sdk-33 --strip-components=1; }
  curl -sSL https://github.com/Kitware/CMake/releases/download/v3.31.8/cmake-3.31.8-linux-x86_64.tar.gz | tar xz -C $C
  mkdir -p $C/ninja-1.12.1-linux-x86_64 && curl -sSL -o /tmp/nj.zip https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-linux.zip \
    && python3 -c "import zipfile;zipfile.ZipFile('/tmp/nj.zip').extractall('$C/ninja-1.12.1-linux-x86_64')" && chmod +x $C/ninja-1.12.1-linux-x86_64/ninja
fi
[ -d maps ] || cambc init --yes >/dev/null
[ -d bots/ga65a6/src ] || python3 -c "import zipfile;zipfile.ZipFile('/mnt/project-files/bot/mybot_ga65a6.zip').extractall('bots/ga65a6')"
for b in ga65a6 study27-economy spar11 spar16; do [ -e bots/$b/.cambc/build/bot-injected.wasm ] || cambc build bots/$b >/dev/null; done
mkdir -p out/sga
cp -rn "$SRC"/. out/sga/
echo "restored into out/sga; last sync $(cat out/sga/last_sync 2>/dev/null)"
