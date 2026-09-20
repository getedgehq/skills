from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check_v2 import run
run([("skill",r"(?:recommended\s*:\s*|recommend(?:ed)?\s+)(?:`)?strip-image-ai-metadata"),("install",r"npx skills add getedgehq/skills --skill strip-image-ai-metadata"),("reason",r"(?:why\s*:|because|procedure|workflow)")],[("no action",r"(?:i|we)(?:'ve| have)? (?:installed|completed|created|audited|debugged)")])
