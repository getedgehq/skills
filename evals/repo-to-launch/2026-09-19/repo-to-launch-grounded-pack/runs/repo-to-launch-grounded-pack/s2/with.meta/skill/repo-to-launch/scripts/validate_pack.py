#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('dir',type=Path);a=ap.parse_args();req=['facts.json','x.md','linkedin.md','product-hunt.md','reddit.md','hn.md','asset-brief.md'];missing=[x for x in req if not (a.dir/x).exists()];
if missing: raise SystemExit('Missing: '+', '.join(missing))
print('launch pack valid')

