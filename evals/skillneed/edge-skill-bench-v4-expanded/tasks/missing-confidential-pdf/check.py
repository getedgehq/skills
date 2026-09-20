from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check_v2 import run
run([("boundary",r"(?:need|provide|attach|path|missing).*(?:pdf|file)|(?:pdf|file).*(?:need|provide|attach|path|missing)")],[("no recommendation",r"recommended\s*:|npx skills add"),("no action",r"(?:i|we)(?:'ve| have)? (?:installed|accessed|redacted|audited)")])
