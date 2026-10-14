# Cambridge Battlecode 2026 (CAMBC 2026a): nuestro bot

Bot en C++ para [CAMBC 2026a](https://2026a.battlecode.co.uk). La versión actual es la **v30** (`bots/v30`),
la misma que está subida a la web como versión 30. Con la v29 llegamos al puesto 25 del ranking.

## Qué hay en el repo

| carpeta | qué es |
|---|---|
| `bots/v30/src/` | el bot: `main.cpp` (draft, farmeo, decisiones de cada campeón), `fight.h` (pelea: kite, hechizos, foco), `params.h` (interruptores) |
| `bots/spar11`, `spar12`, `spar16` | rivales de entrenamiento: el mismo motor con draft de lanzadores (Stellar, Tavi, Cassi&Issac, Willow, Prism). spar12 va en bola, spar16 prioriza matar a los de rango |
| `tools/arena.py` | juega muchas partidas en paralelo y resume victorias, gemas, muertes y kills |
| `tools/variante.sh` | crea una copia de un bot cambiando interruptores de `params.h` y la compila |
| `maps_gen/` | 44 mapas generados al azar, para probar en mapas que nadie ha visto (los mapas de clasificación serán nuevos) |

## Empezar

```bash
pip install cambc                 # CLI oficial
git clone https://github.com/Javiops/Cambridge-Battlecode-2026.git
cd Cambridge-Battlecode-2026
cambc init --yes                  # descarga el SDK, la toolchain y los 9 mapas oficiales en maps/
cambc build bots/v30
cambc run bots/v30 bots/spar11 --map maps/corners.map26a -o out/partida
cambc view out/partida            # ver la repetición
```

## Probar un cambio

1. Crea una variante cambiando interruptores (no toques `bots/v30`):
   ```bash
   tools/variante.sh prueba1 v30 "#define P_FINISH 40"
   ```
   O copia `bots/v30` a `bots/mi_bot` y edita el código.
2. Juégala contra la v30 y contra los rivales, por los dos lados:
   ```bash
   python3 tools/arena.py bots/prueba1 bots/v30    --maps "maps/*.map26a"     --sides both --jobs 4 --no-build --out out/p1_v30
   python3 tools/arena.py bots/prueba1 bots/spar11 --maps "maps/*.map26a"     --sides both --jobs 4 --no-build --out out/p1_s11
   python3 tools/arena.py bots/prueba1 bots/v30    --maps "maps_gen/*.map26a" --sides both --jobs 4 --no-build --out out/p1_gen
   ```
   (quita `--no-build` la primera vez o compila antes con `cambc build`).

Cosas que hemos aprendido probando:
- El motor es determinista: la misma partida sale igual siempre. Un cambio minúsculo puede cambiar varios
  resultados por azar, así que solo cuenta una diferencia clara en muchas partidas.
- Ganar en local no garantiza ganar online: los rivales reales pelean distinto. Por eso existen los spar.
- Usa siempre `maps_gen/` además de los oficiales: la estrategia tiene que salir de cómo es el mapa
  (tamaño del equipo, distancia entre bases, muros, altares), no de un plan para cada mapa.

## Cómo funciona la v30 (resumen)

- **Draft según el mapa** (`P_DRAFTUNI 2`): si el camino entre las dos bases mide 45 casillas o menos es un mapa de
  pelea y elegimos lanzadores como el número 1 del ranking (3 = Cassi&Issac, Ren, Stellar; 4 = + Tavi;
  5 = Ryth, Stellar, Prism, Ren, Tavi). En mapas largos, draft de farmeo: Vendetta, Varg, Cassi&Issac, Ryth, Tavi.
- **Pelea de lanzadores** (`P_KITE`, `P_SWEEP 3`): lanzar hechizos a 4 casillas, quietos, y mantener la distancia.
- **Retirada** (`P_UNI_FLEE 35`, `P_RECALL_NEAR 5`): con menos del 35% de vida se va; hace recall si el enemigo
  más cercano está a 5 o más casillas (el daño corta el recall).
- **Rematar** (`P_FINISH 30`, nuevo en la v30): un enemigo a 6 casillas o menos con menos del 30% de vida se
  persigue aunque huya.
- **Compras** (`P_SHOPUNI 1`): Ren, Prism y Stellar compran foco (power) y algo de vida.
- Todos los interruptores se definen al principio de `main.cpp` (`#ifndef P_...`), casi todos con un comentario. Valen 0 si
  `params.h` no los define.

## Subir una versión

Solo la cuenta del equipo puede subir: `cambc login` y luego `cambc submit bots/NOMBRE`. La versión se activa
desde la web. **Nunca subas al repo el token de login** (se guarda en `~/.config/cambc`, fuera del repo).
