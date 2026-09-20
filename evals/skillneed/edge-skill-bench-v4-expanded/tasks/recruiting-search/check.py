from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check import run
run([("skill",r"recommended\s*:\s*people-search"),("install",r"npx skills add getedgehq/skills --skill people-search"),("why",r"why\s*:")],[("no install claim",r"(?:i|we)(?:'ve| have)? installed")])
