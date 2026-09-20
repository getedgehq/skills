from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "_lib"))
from check import run
run([("covered outcome", r"already covered"), ("names existing package", r"product-launch-video")], [("no recommendation", r"recommended\s*:"), ("no install", r"npx skills add")])
