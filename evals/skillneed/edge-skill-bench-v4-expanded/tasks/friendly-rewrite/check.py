from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check_v2 import run
run([("none",r"(?:no|none|don't|does not|isn't).{0,35}(?:skill|package|needed|need)")],[("no recommendation",r"recommended\s*:|npx skills add"),("no task",r"(?:=\s*61\.2|sessanta|train leaves|summary\s*:|rewritten\s*:)")])
