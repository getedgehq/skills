from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "_lib"))
from check import run
run([("need context", r"need context"), ("identifies access", r"(?:access|connect|mailbox|permission)"), ("asks one question", r"\?")], [("no recommendation", r"recommended\s*:"), ("no install", r"npx skills add")])
