#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHARED=Path(__file__).resolve().parent/'render_card.py'
r=json.loads(Path(sys.argv[1]).read_text())
sign=lambda x:('+' if x>=0 else '')+str(x)
data={
 'eyebrow':'EDGE / SYSTEM PROMPT BATTLE',
 'title':'Does your system prompt work?',
 'subtitle':f"Held-out current vs optimized · {r.get('heldout_tasks','?')} tasks · {r.get('model','same model')}",
 'badge':'DEMO' if r.get('demo') else 'HELD-OUT TEST',
 'metrics':[
   {'label':'Current','value':str(r.get('current_score','unknown'))},
   {'label':'Optimized','value':str(r.get('optimized_score','unknown'))},
   {'label':'Lift','value':sign(r.get('delta',0))},
 ],
 'findings':[
   f"Instruction tokens {sign(r.get('token_delta_pct',0))}%",
   'Same model + same held-out tasks',
   'Optimize behavior, not prompt aesthetics'
 ],
 'footer':'Only verified eval data may replace the DEMO label'
}
assets=ROOT/'assets';assets.mkdir(parents=True,exist_ok=True)
tmp=assets/'.card.json';tmp.write_text(json.dumps(data));subprocess.check_call([sys.executable,str(SHARED),str(tmp),'--svg',str(assets/'system-prompt.svg'),'--png',str(assets/'system-prompt.png')]);tmp.unlink()
