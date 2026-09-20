from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "_lib"))
from check import run
run([("recommendation", r"recommended\s*:\s*http-error-triage"), ("install", r"npx skills add getedgehq/skills --skill http-error-triage"), ("reason", r"why\s*:")], [("no auto-install claim", r"(?:i|we)(?:'ve| have)? installed")])
