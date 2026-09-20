from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check import run
run([("context",r"(?:need context|missing (?:the )?(?:file|pdf)|need (?:the )?(?:file|pdf)|cannot .* without (?:the )?(?:file|pdf))"),("question",r"\?")],[("no recommend",r"recommended\s*:"),("no install",r"npx skills add|getedge install")])
