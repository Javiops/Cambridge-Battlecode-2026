# Panel de rivales: el filtro local que usamos ahora (octubre 2026)

Sirve para probar un cambio del bot en tu ordenador antes de subirlo. La base actual es **v110** (`bots/v110`,
need2-v1, la versión 110 de la web).

## Por qué un panel y no el cara a cara contra la base

Jugar 70 partidas de la variante contra la base no dice nada: cuatro retoques sin ninguna idea detrás dieron
desde 30-40 hasta 38-32, la misma franja que todos los candidatos. Además, online casi nadie juega nuestro draft
(solo el 9% de las partidas son espejo) y los rivales invaden nuestra mitad mucho más que nuestro propio bot.

Por eso el candidato y la base juegan contra **9 rivales** con drafts como los del ranking, en los **40 mapas del
sitio** y por los dos lados (720 partidas por bot). Luego se comparan partida a partida: la misma partida
(rival, mapa, lado) con la base y con el candidato. Solo cuentan las que cambian de resultado, con la barra
`2*sqrt(cambios)`, igual que el juez online.

| rival | draft | notas |
|---|---|---|
| pA | Stellar, Ren, Tavi, Varg, Vendetta | |
| pB | Ryth, Cassi, Vesper, Stellar, Ren | |
| pC | Heart of Ruin, Ren, Ryth, Marcella, Vesper | |
| pInv | nuestro draft | **el invasor**: `P_HALF 250`, mete 3+ campeones en nuestra mitad. Es el que mejor ordenó los veredictos online |
| pD | HoR, Ryth, Vesper, Vendetta, Marcella | banda 91-115 del ranking |
| pF | Ryth, Vesper, Vendetta, Varg, Prism | banda 91-115 |
| pE | Cassi, Ren, Ryth, Stellar, Varg | banda 66-90 |
| pG | Cassi, HoR, Stellar, Tavi, Varg | banda 66-90 |
| pM | espejo (nuestro draft) | |

Todos llevan el cerebro de v82 (`panel/rivals/<nombre>/src`, cambia solo `params.h`). No los edites: si cambian,
los números dejan de ser comparables con la tabla de `CALIBRATION.md`.

## Preparar el ordenador (una vez)

```bash
pip install cambc==3.0.4          # 3.0.4 = motor 1.0.2, el mismo que la web
git clone https://github.com/Javiops/Cambridge-Battlecode-2026.git && cd Cambridge-Battlecode-2026
cambc init --yes                  # SDK, cmake y toolchain (wasi-sdk 33, cmake 3.31.8, ninja 1.12.1)
cambc build bots/v110             # tiene que compilar sin errores
```

Si `cambc init` no consigue descargar la toolchain (pasa detrás de algunos proxys: error de certificado
`UnknownIssuer`), bájala a mano a la caché de cambc (`~/.cache/cambc` en Linux):

```bash
cd ~/.cache/cambc
curl -L https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-33/wasi-sdk-33.0-x86_64-linux.tar.gz | (mkdir -p wasi-sdk-33 && tar xz -C wasi-sdk-33 --strip-components=1)
curl -L https://github.com/Kitware/CMake/releases/download/v3.31.8/cmake-3.31.8-linux-x86_64.tar.gz | tar xz
curl -LO https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-linux.zip && unzip ninja-linux.zip -d ninja-1.12.1-linux-x86_64
```

Para `--gold` y `mech.py` hace falta también `node` (18 o más): decodifican las repeticiones con `tools/replaydump.js`.

Los mapas ya están en el repo: `maps_site40/` son los 40 mapas del pool de la web (22-10-2026, sha verificado).

## Probar un cambio

```bash
mkdir bots/mi_cambio && cp -r bots/v110/src bots/mi_cambio/   # copia solo src/: una carpeta ya compilada no recompila bien
# ... edita bots/mi_cambio/src (un interruptor P_* de params.h si es un umbral)
python3 panel/run.py bots/v110 bots/mi_cambio                  # 1440 partidas la primera vez; la base se reutiliza después
python3 panel/run.py bots/v110 bots/mi_cambio --gold           # + oro en r400 y muertes (para cambios de farmeo)
python3 panel/run.py bots/v110 bots/mi_cambio --rivals pInv --maps elk_arena,the_farm   # prueba rápida
```

Una partida tarda unos 30 s de CPU: con 4 núcleos son unos 12 minutos por bot y con 16 unos 3. Los resultados
se guardan en `out/panel/res/` (no se suben a git). El nombre de cada bot lleva un hash de su `src/`, así que la
base se juega una sola vez y un bot editado nunca reutiliza partidas viejas.

La salida se lee así:

```
mi_cambio-2e631aaf vs v110-0e8c45fe: panel net +7 (40/33, bar 17.1); gems 934 vs 968; deaths 6.5 vs 5.7; games 720 | pA +2 (5/3) ...
```

`40/33` son las partidas que el cambio gana y pierde respecto a la base. El neto (+7) se compara con la barra
(17.1). Con `--gold` sale además `dgold@r400` (oro ganado hasta la ronda 400, respecto a la base) y `ddeaths`.

## Cuándo merece la pena subirlo online

Lo que hemos aprendido calibrando el panel con los veredictos online (tabla completa en `CALIBRATION.md`):

1. Sube a la web si el **neto del panel >= 0 y el invasor (pInv) >= 0**. Si alguno sale negativo por encima
   de su barra, descártalo.
2. **Cambios de farmeo o economía**: el neto del panel no sirve como señal (value, goldw40 y elksplit dieron
   +30, +36 y +21 en el panel y perdieron online). Recházalo si las **muertes por partida suben 0.4 o más** o si
   el **oro en r400 queda por debajo de la base** (`--gold`). El oro temprano es poder de pelea: online, las
   partidas donde el oro en r400 baja 200 o más tienen el doble de muertes.
3. Si el cambio tiene una palanca concreta (por ejemplo, "capturar más campos de oro del medio"), comprueba
   que esa métrica se mueve en las repeticiones del panel (`scripts/mech.py`) antes de subirlo.
4. El juez de verdad es el online emparejado (`online/`): el panel solo filtra.

## Otros scripts (se ejecutan dentro de `out/panel`)

| script | qué mide |
|---|---|
| `scripts/judge.py BASE CAND...` | el veredicto emparejado (lo llama `run.py`); `PAN=pA,pB` limita rivales, `MAPS=a,b` mapas |
| `scripts/gold400.py BASE CAND...` | oro ganado hasta r400 y muertes, partida a partida contra la base |
| `scripts/mech.py cal_BOT_RIVAL` | capturas de alce, campos de solo oro antes de r300, rondas con 2+/3+ rivales en nuestra mitad |
| `scripts/camp.py BOT [pA,pB,...]` | muertes en campamentos frente a muertes por campeones, capturas y oro por partida |
| `scripts/fight.py BOT` | kills, daño por kill, muertes y gemas por partida |
| `scripts/ab.py` | la librería que lee las estadísticas (`res/<tag>/{A,B}_<mapa>.json`) |

Los `TAG`/`BOT` son los nombres con hash que imprime `run.py` (por ejemplo `v110-0e8c45fe`).
