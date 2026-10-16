#!/usr/bin/env python3
"""Genetic algorithm over the macro (farming / economy) genome: tools/ga/ga.py run with tools/ga/macro_genome.py.

usage (from the repo root, after `cambc init --yes`):
  python3 tools/ga/mga.py base                      # bots/ga65a6 = bots/study27-economy + the v44 fight genome
  python3 tools/ga/mga.py prepare                   # instrumented ga65a6 with the macro genome (out/mga)
  python3 tools/ga/mga.py check                     # default macro genome vs the ga65a6 build
  python3 tools/ga/mga.py run --gens 30             # evolve (resumes from out/mga/state.json)
  python3 tools/ga/mga.py validate --top 3
  python3 tools/ga/mga.py export --id ID --out bots/NAME

Every ga.py command and option works; only the defaults differ: genome = macro_genome, work dir out/mga,
base bots/ga65a6 (the bot online as v44; MGA_BASE overrides, e.g. bots/v44x = the online zip with fuel guard and
jackpot), opponents = the base itself (weight 3: farming speed against our own online bot is what self-play judges
well) plus the caster sparring spar16 (weight 1: a macro change that gets us killed shows there; with more weight
the first run learned to beat the casters while losing to the base on sealed maps), training pool = ga.py's plus the generated cousins of the site maps (tools/ga/cousins.py).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import ab  # tools/ab.py: load_stats
import ga
import genome as fight_genome
import macro_genome

BASE = os.environ.get('MGA_BASE', 'bots/ga65a6')
# The fight genome of ga65a6 (GA micro genome 65a6d152b6, online as v44 since 16 Oct 10:46).
GA65A6 = {'P_FLEE_PCT': 29, 'P_UNI_FLEE': 44, 'P_RECALL_PCT': 54, 'P_RECALL_NEAR': 7, 'P_BAIL_PCT': 12,
          'P_AVOID_DIST': 4, 'P_GA_AVOID_HP': 60, 'P_ENGAGE2': 74, 'P_GA_FAV': 83, 'P_GA_KILL_X': 5, 'P_LOWHP': 50,
          'P_GA_SPAWN_HEAL': 87, 'P_FRONT_ZONE': 3, 'P_FRONT_OUT': 145, 'P_KITE_ZONE': 4, 'P_KITE_OUT': 2,
          'P_GA_KITE_HP': 128, 'P_VOLLEY': 43, 'P_CHASE_GEMS': 144, 'P_DANGER': 4, 'P_DANGER_T': 45,
          'P_DANGER_R': 5}
COUSINS = os.environ.get('MGA_COUSINS', '/mnt/project-files/arena/maps/cousins')


def cmd_base(src='bots/study27-economy', out=BASE):
    """bots/ga65a6: the base bot with the v44 fight genome baked in (same as /mnt/project-files/bot/mybot_ga65a6.zip
    plus whatever main added since, e.g. P_MONO)."""
    ga.G = fight_genome
    ga.write_src(src, out, GA65A6, runtime=False)
    ga.G = macro_genome
    print(f'{out}: {src} + fight genome 65a6d152b6')


class _Subprocess:
    """ga.py's subprocess, plus `--json` on `cambc run --statistics` (cambc 2.2 writes binary stats without it)."""
    def __getattr__(self, name):
        return getattr(subprocess, name)

    @staticmethod
    def run(cmd, *a, **k):
        if len(cmd) > 1 and cmd[1] == 'run' and '--statistics' in cmd and '--json' not in cmd:
            cmd = list(cmd) + ['--json']
        if len(cmd) > 1 and cmd[1] == 'run' and os.environ.get('MGA_FUEL'):  # e.g. 10000000: no fuel chaos (checks)
            cmd = list(cmd) + ['--fuel', os.environ['MGA_FUEL']]
        return subprocess.run(cmd, *a, **k)


class _Json:
    """ga.py's json, but a cambc 2.2 statistics file is read into the old flat shape (tools/ab.py load_stats)."""
    def __getattr__(self, name):
        return getattr(json, name)

    @staticmethod
    def load(fp):
        d = json.load(fp)
        if isinstance(d, dict) and 'match' in d and 'outcome' not in d:
            d = ab.load_stats(fp.name)
        return d


def main():
    ga.subprocess = _Subprocess()
    ga.json = _Json()
    ga.G = macro_genome
    ga.OPPS = f'{BASE},bots/spar16'
    ga.TRAIN = ga.TRAIN + [os.path.join(COUSINS, '*.map26a')]
    argv = sys.argv[1:]
    if argv and argv[0] == 'base':
        cmd_base()
        return
    if '--work' not in argv:
        argv = ['--work', 'out/mga'] + argv
    cmd = next((a for a in argv if a in ('prepare', 'check', 'run', 'validate', 'export')), None)
    if cmd == 'prepare' and '--base' not in argv:
        if not os.path.exists(BASE):
            cmd_base()
        argv += ['--base', BASE]
    if cmd == 'run' and '--weights' not in argv and '--opps' not in argv:
        argv += ['--weights', '3,1']
    sys.argv = [sys.argv[0]] + argv
    ga.main()


if __name__ == '__main__':
    main()
