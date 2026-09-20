#!/usr/bin/env python3
import argparse,json,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('repo',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();r=a.repo.resolve();readme=next((x for x in [r/'README.md',r/'README.MD',r/'README'] if x.exists()),None);text=readme.read_text(errors='replace') if readme else ''
title=(re.search(r'^#\s+(.+)$',text,re.M).group(1).strip() if re.search(r'^#\s+(.+)$',text,re.M) else r.name);desc='';
for line in text.splitlines()[1:40]:
 if line.strip() and not line.startswith(('#','!','[','<','```')):desc=line.strip();break
langs={}
SKIP={'.git','__pycache__','node_modules','.venv','.cache','.tmp'}
for f in r.rglob('*'):
 if f.is_file() and not (set(f.parts) & SKIP) and f.stat().st_size<2_000_000:
  ext=f.suffix.lower();langs[ext]=langs.get(ext,0)+1
facts={'repo':str(r),'title':title,'description':desc,'readme':str(readme) if readme else None,'file_count':sum(langs.values()),'top_extensions':sorted(langs.items(),key=lambda x:x[1],reverse=True)[:8],'screenshots':[str(x.relative_to(r)) for x in r.rglob('*') if not (set(x.parts)&SKIP) and x.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}][:20]}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(facts,indent=2))

