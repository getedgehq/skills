from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check import run
run([("none",r"(?:no extra skill needed|no additional (?:skill|package) (?:is )?needed)"),("reason",r"(?:ordinary|simple|direct|translation)")],[("no recommend",r"recommended\s*:"),("no install",r"npx skills add|getedge install")])
