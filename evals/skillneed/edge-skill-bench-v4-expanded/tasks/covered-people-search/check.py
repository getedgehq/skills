from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"_lib")); from check_v2 import run
run([("covered",r"(?:already|currently).{0,30}(?:covered|installed)|(?:covered|installed).{0,30}already"),("existing",r"people-search")],[("no recommendation",r"recommended\s*:|npx skills add")])
