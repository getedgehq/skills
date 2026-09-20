import json
import pathlib
import re
import sys

def run(expected, forbidden=()):
    root=pathlib.Path(sys.argv[1]); text="\n".join(p.read_text(errors="ignore") for p in root.rglob("*") if p.is_file() and p.stat().st_size<1_000_000).lower()
    text=re.sub(r"[*_`]", "", text)
    checks=[(label,bool(re.search(pattern,text,re.I))) for label,pattern in expected]
    checks += [(label,not bool(re.search(pattern,text,re.I))) for label,pattern in forbidden]
    print(json.dumps({"pass":all(ok for _,ok in checks),"score":sum(ok for _,ok in checks)/len(checks),"details":[f"{label}: {'pass' if ok else 'fail'}" for label,ok in checks]}))
