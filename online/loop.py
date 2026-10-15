"""Runs forever: collect new results every 10 minutes and spend the hourly challenge allowance (needs the cookie).
Usage: python3 loop.py [--top 20] [--no-challenge]      (Windows: py loop.py)"""
import subprocess, sys, time, os
here = os.path.dirname(os.path.abspath(__file__)); args = sys.argv[1:]
top = args[args.index('--top') + 1] if '--top' in args else '20'
last_ch = 0
while True:
    subprocess.call([sys.executable, os.path.join(here, 'collect.py')])
    if '--no-challenge' not in args and time.time() - last_ch >= 3600:
        subprocess.call([sys.executable, os.path.join(here, 'challenge.py'), '--top', top]); last_ch = time.time()
    time.sleep(600)
