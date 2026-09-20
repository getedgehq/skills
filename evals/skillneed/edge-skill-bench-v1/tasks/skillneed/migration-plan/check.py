from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "_lib"))
from check import run
run([("recommendation", r"recommended\s*:\s*workplan"), ("install", r"npx skills add getedgehq/skills --skill workplan"), ("reason", r"why\s*:")], [("no auto-install claim", r"(?:i|we)(?:'ve| have)? installed")])
