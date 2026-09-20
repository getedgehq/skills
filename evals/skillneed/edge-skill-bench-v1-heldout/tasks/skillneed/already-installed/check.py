from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check import run
run([("covered",r"(?:already covered|no additional (?:skill|package) (?:is )?needed)"),("existing",r"linkedin-media-prep")],[("no recommend",r"recommended\s*:"),("no install",r"npx skills add|getedge install")])
