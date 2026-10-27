# cf: pkb (pack) + awb (early warning) together
import sys, subprocess
subprocess.check_call(['python3', '/tmp/claude-0/w/opts/pkb.py', sys.argv[1]])
subprocess.check_call(['python3', '/tmp/claude-0/w/opts/awb.py', sys.argv[1]])
