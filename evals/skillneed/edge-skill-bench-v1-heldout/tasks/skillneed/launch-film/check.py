from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check import run
run([("skill",r"recommended\s*:\s*product-launch-video"),("install",r"npx skills add getedgehq/skills --skill product-launch-video"),("why",r"why\s*:")],[("no install claim",r"(?:i|we)(?:'ve| have)? installed")])
