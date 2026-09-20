from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "_lib"))
from check import run
run([("no extra skill", r"no extra skill needed"), ("ordinary task rationale", r"(?:basic|ordinary|direct|arithmetic|calculate)")], [("no recommendation", r"recommended\s*:"), ("no install", r"npx skills add")])
