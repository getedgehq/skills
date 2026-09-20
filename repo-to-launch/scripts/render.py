#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHARED=Path(__file__).resolve().parent/'render_card.py';r=json.loads(Path(sys.argv[1]).read_text())
data={'eyebrow':'EDGE / REPO → LAUNCH','title':r.get('title','Repo in. Launch out.'),'subtitle':r.get('description','')[:90],'badge':'DEMO' if r.get('demo') else 'FACTS FROM REPO','metrics':[{'label':'Launch assets','value':str(r.get('asset_count',6))},{'label':'Repo files','value':str(r.get('file_count','?'))},{'label':'Screenshots found','value':str(len(r.get('screenshots',[])))}], 'findings':['X + LinkedIn copy','Product Hunt + Reddit + HN','Real product asset brief'], 'footer':'No invented traction, capabilities, logos, or benchmarks'}
assets=ROOT/'assets';assets.mkdir(parents=True,exist_ok=True)
tmp=assets/'.card.json';tmp.write_text(json.dumps(data));subprocess.check_call([sys.executable,str(SHARED),str(tmp),'--svg',str(assets/'launch.svg'),'--png',str(assets/'launch.png')]);tmp.unlink()
