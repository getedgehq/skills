#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHARED=Path(__file__).resolve().parent/'render_card.py';r=json.loads(Path(sys.argv[1]).read_text());p=lambda x:f"{100*x:.0f}%"
data={'eyebrow':'EDGE / INVOCATION DOCTOR','title':'Installed ≠ invoked.','subtitle':'Held-out trigger accuracy before vs after','badge':'DEMO' if r.get('demo') else 'HELD-OUT TEST','metrics':[{'label':'Before','value':p(r.get('before_accuracy',0))},{'label':'After','value':p(r.get('after_accuracy',0))},{'label':'Lift','value':('+' if r.get('delta',0)>=0 else '')+p(r.get('delta',0))}], 'findings':['Positive triggers + hard negatives','Description optimized on train split','Result reported on held-out cases'], 'footer':'Do not tune on the held-out set'}
assets=ROOT/'assets';assets.mkdir(parents=True,exist_ok=True)
tmp=assets/'.card.json';tmp.write_text(json.dumps(data));subprocess.check_call([sys.executable,str(SHARED),str(tmp),'--svg',str(assets/'invoke.svg'),'--png',str(assets/'invoke.png')]);tmp.unlink()
